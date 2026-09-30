@echo off
rem Lance MCD2 Item Forge sans fenetre de console, avec l'environnement virtuel du projet.
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
    echo Environnement virtuel introuvable : lance d'abord installer.bat
    pause
    exit /b 1
)
start "" ".venv\Scripts\pythonw.exe" "%~dp0main.py"
