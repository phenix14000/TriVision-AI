import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import threading
import sys
import os

# Ensure we can import sorter
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from sorter import ImageSorter
except ImportError as e:
    print(f"DEBUG IMPORT ERROR: {e}")
    ImageSorter = None

class SorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TriVision Image Sorter")
        self.root.geometry("600x450")
        
        # Style
        bg_color = "#2c3e50"
        fg_color = "#ecf0f1"
        btn_color = "#3498db"
        
        self.root.configure(bg=bg_color)
        
        # Header
        lbl_title = tk.Label(root, text="TriVision AI Sorter", font=("Helvetica", 16, "bold"), bg=bg_color, fg=fg_color)
        lbl_title.pack(pady=10)

        # Folder Selection
        frame_folder = tk.Frame(root, bg=bg_color)
        frame_folder.pack(pady=5, padx=10, fill="x")
        
        tk.Label(frame_folder, text="Dossier Source:", bg=bg_color, fg=fg_color).pack(side="left")
        
        self.entry_path = tk.Entry(frame_folder, width=40)
        self.entry_path.pack(side="left", padx=5, fill="x", expand=True)
        
        btn_browse = tk.Button(frame_folder, text="...", command=self.browse_folder, bg=btn_color, fg="white")
        btn_browse.pack(side="left")

        # Options
        frame_opts = tk.Frame(root, bg=bg_color)
        frame_opts.pack(pady=10)
        
        self.move_mode = tk.BooleanVar(value=False)
        chk_move = tk.Checkbutton(frame_opts, text="Déplacer les fichiers (au lieu de copier)", variable=self.move_mode, bg=bg_color, fg=fg_color, selectcolor="#34495e")
        chk_move.pack()

        # Action Button
        self.btn_start = tk.Button(root, text="Démarrer le Tri", command=self.start_thread, font=("Helvetica", 12, "bold"), bg="#27ae60", fg="white", height=2)
        self.btn_start.pack(pady=10, fill="x", padx=20)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(root, height=10, bg="#34495e", fg="#bdc3c7", font=("Consolas", 9))
        self.log_area.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.sorter = None

    def log(self, msg):
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)

    def browse_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.entry_path.delete(0, tk.END)
            self.entry_path.insert(0, path)

    def start_thread(self):
        source_dir = self.entry_path.get()
        if not source_dir or not os.path.exists(source_dir):
            messagebox.showerror("Erreur", "Veuillez sélectionner un dossier valide.")
            return
            
        self.btn_start.config(state="disabled", text="Tri en cours...")
        self.log("Initialisation des modèles IA... (Cela peut prendre quelques minutes au premier lancement)")
        
        # Redirect stdout/stderr
        sys.stdout = PrintLogger(self.log_area)
        sys.stderr = PrintLogger(self.log_area)
        
        thread = threading.Thread(target=self.run_process, args=(source_dir,))
        thread.daemon = True
        thread.start()

    def run_process(self, source_dir):
        try:
            if not self.sorter:
                if ImageSorter:
                    print("Tentative de chargement de sorter.py...")
                    self.sorter = ImageSorter()
                else:
                    self.log("Erreur: Impossible d'importer sorter.py. Module manquant (utilisez-vous le venv ?). Regardez la console pour le détail.")
                    self.root.after(0, self.reset_ui)
                    return

            if not self.sorter.style_classifier and not self.sorter.anime_ai_classifier and not self.sorter.photo_ai_classifier:
                 self.log("ATTENTION: Aucun modèle n'a pu être chargé. Vérifiez votre connexion internet ou les logs ci-dessus.")
                 print("Critical: No models loaded.")

            mode = 'move' if self.move_mode.get() else 'copy'
            
            self.log(f"Début du tri dans: {source_dir}")
            self.sorter.sort_directory(source_dir, mode=mode)
            
            self.log("Terminé !")
            messagebox.showinfo("Succès", "Tri terminé !")
            
        except Exception as e:
            self.log(f"Erreur globale: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erreur", str(e))
        finally:
            self.root.after(0, self.reset_ui)

    def reset_ui(self):
        self.btn_start.config(state="normal", text="Démarrer le Tri")
        # Restore stdout? Maybe not needed if we want persistent logs, 
        # but good practice if we were a larger app. 
        # For this simple tool, keep it redirected or don't bother restoring.

class PrintLogger: 
    def __init__(self, text_widget): 
        self.text_widget = text_widget 
 
    def write(self, message): 
        self.text_widget.after(0, self.append_text, message) 
 
    def append_text(self, message): 
        self.text_widget.insert(tk.END, message) 
        self.text_widget.see(tk.END)
        
    def flush(self): 
        pass

if __name__ == "__main__":
    if not ImageSorter:
        print("Erreur critique: sorter.py manquant")
    
    root = tk.Tk()
    app = SorterApp(root)
    root.mainloop()
