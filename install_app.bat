@echo off
setlocal
title TriVision AI Installer

echo ==================================================
echo     INSTALLATION DE TRIVISION AI
echo ==================================================
echo.

:: 1. GIT CLONE (Placeholder - Replace URL)
echo 1/3 Clonage du depot...
:: Remplacez l'URL ci-dessous par votre depot Git reel
git clone https://github.com/EXEMPLE/TriVision.git
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors du clonage. Verifiez l'URL ou si Git est installe.
    pause
    exit /b
)

:: Enter the directory (Assumes directory name is the repo name, adjust if needed)
if exist "TriVision" (
    cd TriVision
) else (
    echo Le dossier TriVision n'a pas ete trouve. Peut-etre etes-vous deja dedans ?
)

:: 2. CREATE VENV
echo.
echo 2/3 Creation de l'environnement virtuel...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo Echec de la creation du venv. Verifiez que Python est installe et dans le PATH.
    pause
    exit /b
)

:: 3. INSTALL REQUIREMENTS
echo.
echo 3/3 Installation des dependances (Cela peut prendre un moment)...
call venv\Scripts\activate.bat
pip install --upgrade pip
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Erreur lors de l'installation des dependances.
    pause
    exit /b
)

echo.
echo ==================================================
echo     INSTALLATION SUCCES !
echo ==================================================
echo Vous pouvez maintenant lancer l'application avec start.bat
echo.
pause
