# 👁️ TriVision AI - Universal Image Sorter

**TriVision AI** is a powerful local application designed to sort your image collections automatically using AI models. It features a modern web interface (Gradio) and supports custom model training.

## 🚀 Key Features

*   **Automatic Sorting**: Classify thousands of images in seconds (Manga vs Real, or any custom categories).
*   **GPU Acceleration**: Fully supports NVIDIA CUDA for blazing fast processing.
*   **Custom Training**: Train your own AI models (Fine-Tuning) directly from the UI.
    *   **Single-Source Mode**: Point to a root dataset folder (e.g., `Data/Cat`, `Data/Dog`).
    *   **Multi-Source Mode**: Combine up to 30 different folders as categories.
*   **User Friendly**:
    *   One-click installation via `install_app.bat`.
    *   Modern "Ocean" theme interface.
    *   Real-time progress bars.
*   **100% Local**: No data sent to the cloud.

---

## 🛠️ Installation

### Prerequisites
*   **Windows 10/11**
*   **Python 3.10+** installed.
*   **Git** installed.

### Quick Start
1.  Double-click on **`install_app.bat`**.
    *   It will create the virtual environment and install all dependencies (Torch, Transformers, Gradio...).
2.  Once finished, double-click on **`start.bat`** to launch the application.

*Alternative Manual Install:*
```bash
python -m venv venv
.\venv\Scripts\pip install -r requirements.txt
.\start.bat
```

---

## 📖 Usage

### 1. 🖼️ Image Sorting (Tri Images)
1.  Go to the **"Tri Images"** tab.
2.  **Select a Model**: Default is *Manga/Real*, or choose your custom trained model.
3.  **Select Source Folder**: The folder containing images to sort.
4.  **Options**: Check "Déplacer" to move files instead of copying.
5.  Click **"🚀 Démarrer le Tri"**.

### 2. 🧠 Training (Entraînement)
Create your own AI model to recognize your specific categories.

*   **Mode 1 Source (Root Dataset)**:
    *   Use this if you have a folder structure like `MyData/Cat` and `MyData/Dog`.
    *   Select "1" Source, give a Model Name, and point to `MyData`.
*   **Mode Multi-Sources (2+)**:
    *   Use this if your folders are scattered.
    *   Select "2" (or more) Sources.
    *   For each line, give a Category Name (e.g., "Car") and point to the folder.

---

## 🇫🇷 Version Française

**TriVision AI** est une application locale puissante pour trier automatiquement vos collections d'images grâce à l'IA.

### Fonctionnalités
*   **Tri Automatique** : Triez des milliers d'images rapidement.
*   **Entraînement Personnalisé** : Créez vos propres modèles IA (jusqu'à 30 catégories).
*   **Interface Moderne** : Facile à utiliser grâce à Gradio (Thème Ocean).
*   **Respect de la vie privée** : Tout tourne en local sur votre PC.

### Installation
1.  Lancez **`install_app.bat`** pour tout installer automatiquement.
2.  Lancez **`start.bat`** pour ouvrir l'application.

---

## 📜 License

This project is licensed under the **MIT License**.

```text
MIT License

Copyright (c) 2024 TriVision AI

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```
