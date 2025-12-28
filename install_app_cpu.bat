@echo off
setlocal
title TriVision AI Installer

echo ==================================================
echo     INSTALLATION DE TRIVISION AI
echo ==================================================
echo.

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
