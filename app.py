import gradio as gr
import os
from sorter import ImageSorter, train_model
import tkinter as tk
from tkinter import filedialog
import pandas as pd

# Global Sorter
sorter = ImageSorter(model_name="default")

def get_available_models():
    models_dir = os.path.join(os.getcwd(), "Models")
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
    models = ["default (Manga/Real)"]
    for d in os.listdir(models_dir):
        if os.path.isdir(os.path.join(models_dir, d)):
            models.append(d)
    return models

def open_folder_dialog():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    folder_path = filedialog.askdirectory()
    root.destroy()
    return folder_path

def update_model_dropdown():
    return gr.Dropdown(choices=get_available_models())

def on_model_change(model_name):
    global sorter
    real_name = "default" if "default" in model_name else model_name
    sorter = ImageSorter(model_name=real_name)
    return f"Modèle chargé : {real_name}"

def run_sort(folder, manga_out, photo_out, move_files, model_name):
    if not folder:
        return "Veuillez sélectionner un dossier source."
    real_name = "default" if "default" in model_name else model_name
    if sorter.model_name != real_name:
        on_model_change(model_name)
    mode = 'move' if move_files else 'copy'
    return sorter.sort_directory(folder, mode=mode, manga_out=manga_out, photo_out=photo_out)

# --- NEW TRAINING LOGIC ---

def update_rows_visibility(num_cats):
    # Returns a list of updates for the Rows visibility + Help Box visibility
    idx = int(num_cats)
    updates = []
    for i in range(30): # MAX 30
        if i < idx:
            updates.append(gr.Row(visible=True))
        else:
            updates.append(gr.Row(visible=False))
    
    # Logic for Help Box (Last element in updates list)
    # Visible only if idx == 1
    if idx == 1:
        updates.append(gr.Markdown(visible=True))
    else:
        updates.append(gr.Markdown(visible=False))
        
    return updates

def run_train_fixed_rows(epochs, batch, *args):
    # args: [name0, path0, name1, path1, ...]
    
    sources_list = []
    class_names = []
    
    for i in range(30):
        c_name = args[i*2]
        c_path = args[i*2 + 1]
        
        if c_path and str(c_path).strip():
             final_name = str(c_name).strip() if c_name else f"Class_{i+1}"
             # If name empty, try to derive from path for the Model Name generation
             if not c_name:
                 final_name = os.path.basename(os.path.normpath(c_path))
                 
             sources_list.append({'class_name': final_name, 'path': c_path})
             class_names.append(final_name)
    
    if len(sources_list) == 0:
        return "Erreur : Aucune catégorie valide renseignée."
    
    # Auto-generate Model Name
    # Limit to e.g. 50 chars to avoid filesystem issues
    raw_name = "_".join(class_names)
    
    # SPECIAL CASE: Single Source = Root Dataset
    # If user provided 1 source, we MUST assume it's a dataset containing subfolders.
    # We use the provided name (if any) as the MODEL name, but we clear the class_name in the dict
    # so proper subfolder scanning is triggered in sorter.py.
    if len(sources_list) == 1:
        sources_list[0]['class_name'] = "" # Force auto-detect
        # If user typed a name, use it for the model. If not, use folder name.
        if class_names[0]:
            raw_name = class_names[0]
            
    import re
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '', raw_name)
    model_name = safe_name[:50]
    
    return train_model(model_name, sources_list, int(epochs), int(batch))


# CSS
css = """
.container { max-width: 900px; margin: auto; }
.path-row { align-items: center; gap: 10px; }
.compact-input { max-width: 400px !important; } 
/* Hide Spinners for number inputs */
/* Hide Spinners for number inputs */
input[type=number]::-webkit-inner-spin-button, 
input[type=number]::-webkit-outer-spin-button { 
  -webkit-appearance: none; 
  margin: 0; 
}
input[type=number] {
  -moz-appearance: textfield; 
}
.align-end { align-items: flex-end !important; }
"""

# UI
with gr.Blocks(title="TriVision AI") as demo:

    gr.Markdown("# 👁️ TriVision AI - Universal Sorter", elem_classes=["title"])
    
    with gr.Tabs():
        # --- TAB 1: CLASSIFIER ---
        with gr.Tab("🖼️ Tri Images"):
            gr.Markdown("### 1. Configuration")
            with gr.Row():
                with gr.Column(scale=1):
                    with gr.Row(elem_classes=["align-end"]):
                        model_selector = gr.Dropdown(label="Choisir le Modèle IA", choices=get_available_models(), value="default (Manga/Real)", interactive=True, scale=4)
                        refresh_btn = gr.Button("🔄", scale=0, min_width=40)
                with gr.Column(scale=1):
                    pass # Spacer

            gr.Markdown("### 2. Sélection des Dossiers")
            with gr.Group():
                with gr.Row(elem_classes=["path-row"]):
                    input_dir = gr.Textbox(label="Dossier Source", placeholder="Le dossier contenant les images...", scale=10, show_label=False, container=False, max_lines=1)
                    btn_browse_in = gr.Button("📂", scale=0, min_width=40)

                with gr.Accordion("Options de Sortie (Mode Défaut)", open=False):
                    gr.Markdown("Uniquement pour le modèle default.")
                    with gr.Row(elem_classes=["path-row"]):
                        manga_out = gr.Textbox(label="Dossier Manga", placeholder="Optionnel...", scale=10, show_label=False, container=False, max_lines=1)
                        btn_browse_manga = gr.Button("📂", scale=0, min_width=40)
                    with gr.Row(elem_classes=["path-row"]):
                        photo_out = gr.Textbox(label="Dossier Photo", placeholder="Optionnel...", scale=10, show_label=False, container=False, max_lines=1)
                        btn_browse_photo = gr.Button("📂", scale=0, min_width=40)

            gr.Markdown("### 3. Options de Tri")
            move_chk = gr.Checkbox(label="Déplacer les fichiers", value=False)
            sort_btn = gr.Button("🚀 Démarrer le Tri", variant="primary", size="lg")
            output_log = gr.Textbox(label="Logs", lines=8, interactive=False)
            
            # Sub-Events
            refresh_btn.click(fn=update_model_dropdown, outputs=model_selector)
            model_selector.change(fn=on_model_change, inputs=model_selector, outputs=output_log)
            btn_browse_in.click(fn=open_folder_dialog, outputs=input_dir)
            btn_browse_manga.click(fn=open_folder_dialog, outputs=manga_out)
            btn_browse_photo.click(fn=open_folder_dialog, outputs=photo_out)
            sort_btn.click(fn=run_sort, inputs=[input_dir, manga_out, photo_out, move_chk, model_selector], outputs=output_log)

        # --- TAB 2: TRAINING ---
        with gr.Tab("🧠 Entraînement"):
            gr.Markdown("### Créateur de Modèle IA")
            gr.Markdown("Choisissez le mode de sources : **1** = Un dossier contenant déjà des sous-dossiers (Dataset complet). **2+** = Vous sélectionnez chaque dossier catégorie par catégorie.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    # Generate choices 1 to 30
                    choices_list = [str(x) for x in range(1, 31)]
                    nb_cats_dd = gr.Dropdown(label="Nombre de Sources", choices=choices_list, value="1", interactive=True)
                with gr.Column(scale=3):
                    # Warning / Help message that toggles
                    help_box = gr.Markdown(
                        """
                        > **⚠️ Mode 1 Source (Dataset Racine)**
                        > Votre dossier DOIT contenir des **sous-dossiers** pour chaque catégorie.
                        > *Exemple : `MonDossier/Chat`, `MonDossier/Chien`...*
                        > Si votre dossier contient juste des images, ça ne marchera pas.
                        """,
                        visible=True
                    )
            
            # Fixed Rows Container
            cat_rows = []
            
            # Create 30 rows
            for i in range(30):
                visible = True if i < 1 else False
                with gr.Row(visible=visible, elem_classes=["path-row"]) as row:
                    # Logic to change placeholder based on index could be complex dynamically, 
                    # so we keep generic placeholders but clarify inMarkdown above.
                    c_name = gr.Textbox(label=f"Nom (Modèle)", placeholder="", scale=3, max_lines=1)
                    c_path = gr.Textbox(show_label=False, placeholder="Chemin du dossier racine...", scale=6, container=False, max_lines=1)
                    c_browse = gr.Button("📂", scale=0, min_width=40)
                    
                    c_browse.click(fn=open_folder_dialog, outputs=c_path)
                    cat_rows.append((row, c_name, c_path))
            
            # Collect components
            all_row_containers = [r[0] for r in cat_rows]
            
            all_train_inputs = []
            for r in cat_rows:
                all_train_inputs.append(r[1])
                all_train_inputs.append(r[2])
            
            # Visibility Change
            nb_cats_dd.change(fn=update_rows_visibility, inputs=nb_cats_dd, outputs=all_row_containers + [help_box])
            
            # Settings
            with gr.Row():
                epochs = gr.Slider(label="Epochs", minimum=1, maximum=20, value=3, step=1)
                batch = gr.Slider(label="Batch Size", minimum=1, maximum=32, value=4, step=1)
            
            train_btn = gr.Button("🦾 Lancer l'Entraînement", variant="primary", size="lg")
            train_log = gr.Textbox(label="Résultat", lines=10)
            
            train_btn.click(
                fn=run_train_fixed_rows,
                inputs=[epochs, batch] + all_train_inputs,
                outputs=train_log
            )

if __name__ == "__main__":
    demo.queue().launch(inbrowser=True, theme=gr.themes.Ocean(), css=css)
