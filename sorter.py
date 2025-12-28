import os
import shutil
import torch
from transformers import pipeline, AutoModelForImageClassification, AutoFeatureExtractor, TrainingArguments, Trainer, AutoImageProcessor
from datasets import load_dataset, Image
import glob
from torchvision import transforms

class ImageSorter:
    def __init__(self, model_name="default"):
        self.device = 0 if torch.cuda.is_available() else -1
        self.model_name = model_name
        self.base_model_path = os.path.join(os.getcwd(), "Models")
        
        print(f"Initializing Sorter with model: {self.model_name}")
        self.classifier = self._load_model()

    def _load_model(self):
        """Loads the specified model pipeline."""
        try:
            if self.model_name == "default":
                # Fallback / Default Legacy Model
                try:
                    return pipeline("image-classification", model="deepghs/anime_real_cls", device=self.device, trust_remote_code=True)
                except Exception:
                    # Silent fallback
                    return pipeline("image-classification", model="google/vit-base-patch16-224", device=self.device)
            else:
                # Custom Model from Models/ folder
                model_path = os.path.join(self.base_model_path, self.model_name)
                print(f"Loading custom model from: {model_path}")
                if not os.path.exists(model_path):
                    # Try current directory for legacy 'my_custom_model'
                    if self.model_name == "my_custom_model" and os.path.exists("my_custom_model"):
                        model_path = "my_custom_model"
                    else:
                        raise FileNotFoundError(f"Model {self.model_name} not found in {self.base_model_path}")
                
                return pipeline("image-classification", model=model_path, device=self.device)
        except Exception as e:
            print(f"Error loading model {self.model_name}: {e}")
            return None

    def classify_image(self, image_path):
        if not self.classifier:
            return None
        try:
            results = self.classifier(image_path)
            # results is like [{'label': 'Manga', 'score': 0.99}, ...]
            return results[0]['label']
        except Exception as e:
            print(f"Error classifying {image_path}: {e}")
            return None

    def sort_directory(self, source_dir, mode='copy', progress_callback=None, manga_out=None, photo_out=None):
        source_dir = os.path.abspath(source_dir)
        files = [f for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.bmp'))]
        
        from tqdm import tqdm
        
        # print("Sorting started...") # Optional
        
        results_log = []
        # Use tqdm for progress bar in CMD
        iterator = tqdm(files, desc="Sorting Images", unit="img")
        
        for i, filename in enumerate(iterator):
            filepath = os.path.join(source_dir, filename)
            label = self.classify_image(filepath)
            
            if label:
                # Determine destination
                if self.model_name == "default" and (manga_out or photo_out):
                    if ("Manga" in label or "anime" in label) and manga_out:
                        dest_folder = manga_out
                    elif ("Photo" in label or "real" in label) and photo_out:
                        dest_folder = photo_out
                    else:
                        dest_folder = os.path.join(source_dir, label)
                else:
                    dest_folder = os.path.join(source_dir, label)

                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                
                dest_path = os.path.join(dest_folder, filename)
                
                try:
                    if mode == 'move':
                        shutil.move(filepath, dest_path)
                    else:
                        shutil.copy2(filepath, dest_path)
                    results_log.append(f"{filename} -> {label}")
                except Exception as e:
                    print(f"Error moving/copying {filename}: {e}")
                    results_log.append(f"Error {filename}: {e}")
            
        return "\n".join(results_log[:20]) + ("\n..." if len(results_log) > 20 else "") + f"\n\nTraitement de {len(files)} images terminé."

    def train_model_multi(self, sources_list, epochs=3, batch_size=4):
        """
        sources_list: List of dicts [{'class_name': 'Manga', 'path': '/path/to/manga'}, ...]
        If class_name is empty/None, assumes path is a Root Dataset (contains subfolders).
        """
        print(f"Starting training with sources: {sources_list}")
        
        # Temp dir for aggregation
        temp_dir = os.path.join(os.getcwd(), "temp_training_data")
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
        os.makedirs(temp_dir)
        
        try:
            # 1. Aggregate Data
            for source in sources_list:
                path = source.get('path')
                class_name = source.get('class_name')
                
                if not path or not os.path.exists(path):
                    continue
                
                if class_name:
                    # Explicit Class: Copy content of path to temp/class_name
                    dst = os.path.join(temp_dir, class_name)
                    os.makedirs(dst, exist_ok=True)
                    
                    # Copy images
                    for item in os.listdir(path):
                        s = os.path.join(path, item)
                        if os.path.isfile(s) and s.lower().endswith(('.jpg', '.png', '.jpeg', '.webp')):
                            shutil.copy2(s, os.path.join(dst, item))
                    
                    # Also check for subdirs? No, user said "Type dataset name" -> implies leaf folder.
                    # But if they point to a folder that HAS subfolders, maybe we should warn? 
                    # For now, let's assume leaf images.
                    
                else:
                    # Root Dataset: Copy subfolders to temp/
                    subdirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
                    for sub in subdirs:
                        src = os.path.join(path, sub)
                        dst = os.path.join(temp_dir, sub)
                        if not os.path.exists(dst):
                            shutil.copytree(src, dst)
                        else:
                            # Merge
                            for item in os.listdir(src):
                                s = os.path.join(src, item)
                                d = os.path.join(dst, item)
                                if os.path.isfile(s):
                                    shutil.copy2(s, d)

            # 2. Check Aggregation
            classes = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d))]
            # Filter out empty classes
            classes = [c for c in classes if len(os.listdir(os.path.join(temp_dir, c))) > 0]
            
            if len(classes) < 2:
                return f"Erreur: Données insuffisantes pour l'entraînement.\nClasses trouvées : {classes}.\nIl faut au moins 2 catégories avec des images."

            # 3. Train
            base_model = "google/vit-base-patch16-224-in21k"
            output_dir = os.path.join(os.getcwd(), "Models", self.model_name) if self.model_name != "default" else "my_custom_model"
            
            dataset = load_dataset("imagefolder", data_dir=temp_dir, split="train")
            try:
                split = dataset.train_test_split(test_size=0.1)
                train_ds = split['train']
                val_ds = split['test']
            except:
                # Not enough data for split? Use same for both (bad practice but avoids crash)
                train_ds = dataset
                val_ds = dataset
            
            labels = train_ds.features['label'].names
            label2id = {label: str(i) for i, label in enumerate(labels)}
            id2label = {str(i): label for i, label in enumerate(labels)}

            processor = AutoImageProcessor.from_pretrained(base_model)
            def transforms_fn(examples):
                examples["pixel_values"] = [processor(img.convert("RGB"), return_tensors="pt")["pixel_values"][0] for img in examples["image"]]
                return examples
            
            train_ds.set_transform(transforms_fn)
            val_ds.set_transform(transforms_fn)

            model = AutoModelForImageClassification.from_pretrained(
                base_model,
                num_labels=len(labels),
                id2label=id2label,
                label2id=label2id,
                ignore_mismatched_sizes=True
            )

            training_args = TrainingArguments(
                output_dir=output_dir,
                per_device_train_batch_size=int(batch_size),
                num_train_epochs=int(epochs),
                remove_unused_columns=False,
                eval_strategy="steps", # Change to steps if dataset small
                save_strategy="steps",
                save_steps=100,
                eval_steps=100,
                learning_rate=5e-5,
                load_best_model_at_end=True,
                save_total_limit=1,
                use_cpu=False if torch.cuda.is_available() else True
            )

            def collate_fn(batch):
                return {
                    'pixel_values': torch.stack([x['pixel_values'] for x in batch]),
                    'labels': torch.tensor([x['label'] for x in batch])
                }

            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_ds,
                eval_dataset=val_ds,
                tokenizer=processor,
                data_collator=collate_fn,
            )

            trainer.train()
            trainer.save_model(output_dir)
            processor.save_pretrained(output_dir)
            
            # Cleanup
            try:
                shutil.rmtree(temp_dir)
            except: 
                pass

            return f"Entraînement terminé ! Modèle '{self.model_name}' sauvegardé.\nClasses apprises : {', '.join(labels)}"

        except Exception as e:
            import traceback
            traceback.print_exc()
            return f"Echec: {e}"

# Global wrapper
def train_model(model_name, sources_list, epochs=3, batch_size=4):
    s = ImageSorter(model_name=model_name)
    return s.train_model_multi(sources_list, epochs, batch_size)
