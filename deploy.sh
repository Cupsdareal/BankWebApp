#!/bin/bash

# Variables
REPO_URL="https://github.com/Cupsdareal/BankWebApp.git"
DEPLOY_DIR="$HOME/CoursObjet/ciCd/app"
BACKEND_DIR="$DEPLOY_DIR/backend"
FRONTEND_DIR="$DEPLOY_DIR/frontend"
INSTANCE_DIR="$DEPLOY_DIR/instance"

# Étape 1 : Installer Chocolatey (si non installé)
if ! command -v choco &> /dev/null; then
    echo "Installation de Chocolatey..."
    sudo apt-get update
    sudo apt-get install -y curl
    curl -fsSL https://chocolatey.org/install.sh | sudo bash
fi

# Étape 2 : Installer les dépendances système
echo "Mise à jour des dépendances système..."
sudo apt-get update
sudo apt-get install -y git python3 python3-venv nodejs npm

# Étape 3 : Cloner le dépôt Git
echo "Clonage du dépôt Git..."
if [ -d "$DEPLOY_DIR" ]; then
    echo "Le répertoire de déploiement existe déjà. Suppression..."
    rm -rf "$DEPLOY_DIR"
fi
git clone "$REPO_URL" "$DEPLOY_DIR"

# Étape 4 : Backend - Installer les dépendances et démarrer l'application Flask
echo "Déploiement du backend..."
cd "$BACKEND_DIR"
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
# Lancer le serveur
python app.py &

# Étape 5 : Frontend - Installer les dépendances et construire l'application
echo "Déploiement du frontend..."
cd "$FRONTEND_DIR"
npm install
npm run build
# Lancer le serveur frontend
python3 -m http.server 8000 &

echo "Déploiement terminé !"