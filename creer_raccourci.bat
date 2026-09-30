@echo off
rem Cree le raccourci "MCD2 Item Forge" sur le bureau, avec l'icone de l'application.
rem Ajoute --menu-demarrer apres le nom du script pour l'ajouter aussi au menu Demarrer.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Environnement virtuel introuvable : lance d'abord installer.bat
    pause
    exit /b 1
)
".venv\Scripts\python.exe" "%~dp0tools\creer_raccourci.py" %*
pause
