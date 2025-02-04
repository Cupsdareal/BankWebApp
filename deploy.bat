@echo off

:: Variables
set REPO_URL=https://github.com/Cupsdareal/BankWebApp.git
set DEPLOY_DIR=C:\CoursObjet\ciCd\app
set BACKEND_DIR=%DEPLOY_DIR%\backend
set FRONTEND_DIR=%DEPLOY_DIR%\frontend
set INSTANCE_DIR=%DEPLOY_DIR%\instance

:: Étape 1 : Installer Chocolatey (si non installé)
where choco >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Installation de Chocolatey...
    @"%SystemRoot%\System32\WindowsPowerShell\v1.0\powershell.exe" -NoProfile -InputFormat None -ExecutionPolicy Bypass -Command "iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))" && SET "PATH=%PATH%;%ALLUSERSPROFILE%\chocolatey\bin"
)

:: Étape 2 : Installer les dépendances système
echo Mise à jour des dépendances système...
choco install git python nodejs -y

:: Étape 3 : Cloner le dépôt Git
echo Clonage du dépôt Git...
if exist "%DEPLOY_DIR%" (
    echo Le répertoire de déploiement existe déjà. Suppression...
    rmdir /s /q "%DEPLOY_DIR%"
)
git clone %REPO_URL% "%DEPLOY_DIR%"

:: Étape 4 : Backend - Installer les dépendances et démarrer l'application Flask
echo Déploiement du backend...
cd "%BACKEND_DIR%"
python -m venv venv
call venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
:: Lancer le server 
python app.py


:: Étape 5 : Frontend - Installer les dépendances et construire l'application
echo Déploiement du frontend...
cd "%FRONTEND_DIR%"
npm install
npm run build
:: lancer le serveur frontend 
 python -m http.server 8000

echo Déploiement terminé !