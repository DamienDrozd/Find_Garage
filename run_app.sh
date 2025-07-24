#!/bin/bash

# Script pour activer l'environnement virtuel et lancer l'application

if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "🔧 Lancez d'abord : ./install_dependencies.sh"
    exit 1
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  Fichier .env non trouvé."
    echo "📋 Configuration avec SQLite par défaut..."
    echo "💡 Pour PostgreSQL, créez un fichier .env basé sur .env.example"
    echo ""
fi

# Lancer l'application
echo "🚀 Lancement de l'application Streamlit..."
streamlit run analyse_streamlit.py
