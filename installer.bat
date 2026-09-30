@echo off
rem Cree l'environnement virtuel .venv et installe les dependances de MCD2 Item Forge.
setlocal
cd /d "%~dp0"

rem Choix de l'interpreteur : installation utilisateur de Python 3.12, puis lanceur py, puis python.
set "PYEXE=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
set "PYARGS="
if exist "%PYEXE%" goto venv
where py >nul 2>nul
if not errorlevel 1 (
    set "PYEXE=py"
    set "PYARGS=-3.12"
    goto venv
)
set "PYEXE=python"

:venv
echo [1/2] Creation de l'environnement virtuel .venv ...
"%PYEXE%" %PYARGS% -m venv .venv
if errorlevel 1 goto error

echo [2/2] Installation des dependances ...
".venv\Scripts\python.exe" -m pip install --upgrade pip
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto error

echo.
echo Installation terminee. Lance l'application avec lancer.bat
pause
exit /b 0

:error
echo.
echo Echec de l'installation. Verifie que Python 3.12 64 bits est installe (voir README).
pause
exit /b 1
