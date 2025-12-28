@echo off
cd /d "%~dp0"
echo Lancement de TriVision...
echo Activation de l'environnement virtuel...
if exist venv\Scripts\python.exe (
    "venv\Scripts\python.exe" app.py
) else (
    echo Erreur : Environnement virtuel venv introuvable.
    echo Veuillez executer : python -m venv venv && .\venv\Scripts\pip install -r requirements.txt
    pause
)
pause
