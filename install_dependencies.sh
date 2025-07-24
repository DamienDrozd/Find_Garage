#!/bin/bash

echo "🚀 Installation des dépendances pour la migration PostgreSQL..."
echo ""

# Vérifier si python3-venv est installé
if ! python3 -c "import venv" 2>/dev/null; then
    echo "📦 Installation de python3-venv..."
    sudo apt update
    sudo apt install -y python3-venv python3-full
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "🔧 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔄 Activation de l'environnement virtuel..."
source venv/bin/activate

# Mise à jour pip
echo "⬆️  Mise à jour de pip..."
pip install --upgrade pip

# Installation des packages
echo "📚 Installation des dépendances..."
pip install -r requirements.txt

echo ""
echo "✅ Installation terminée !"
echo ""
echo "📋 Pour utiliser l'application :"
echo "1. Activez l'environnement virtuel : source venv/bin/activate"
echo "2. Copiez .env.example vers .env : cp .env.example .env"
echo "3. Modifiez DATABASE_URL dans .env avec vos paramètres PostgreSQL"
echo "4. Testez la connexion : python test_database.py"
echo "5. Lancez l'application : streamlit run analyse_streamlit.py"
echo ""
echo "💡 Pour désactiver l'environnement virtuel : deactivate"
