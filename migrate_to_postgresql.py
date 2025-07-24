#!/usr/bin/env python3
"""
Script de migration des données de SQLite vers PostgreSQL

Usage: 
    source venv/bin/activate
    python migrate_to_postgresql.py
"""

import sqlite3
import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def migrate_sqlite_to_postgresql():
    """Migre les données de SQLite vers PostgreSQL"""
    
    # Charger les variables d'environnement
    load_dotenv()
    
    sqlite_file = "resultats_batiments.sqlite"
    postgresql_url = os.getenv('DATABASE_URL')
    
    if not postgresql_url:
        print("❌ Erreur : DATABASE_URL n'est pas définie dans le fichier .env")
        return False
    
    # Correction pour les URLs PostgreSQL avec le dialecte 'postgres'
    if postgresql_url.startswith('postgres://'):
        postgresql_url = postgresql_url.replace('postgres://', 'postgresql://', 1)
    
    if not postgresql_url.startswith('postgresql'):
        print("❌ Erreur : DATABASE_URL doit pointer vers une base PostgreSQL")
        return False
    
    if not os.path.exists(sqlite_file):
        print(f"❌ Erreur : Le fichier SQLite {sqlite_file} n'existe pas")
        return False
    
    try:
        # Connexion SQLite
        print("📄 Lecture des données depuis SQLite...")
        sqlite_conn = sqlite3.connect(sqlite_file)
        df = pd.read_sql_query("SELECT * FROM validation", sqlite_conn)
        sqlite_conn.close()
        
        print(f"✅ {len(df)} enregistrements trouvés dans SQLite")
        
        if len(df) == 0:
            print("ℹ️  Aucune donnée à migrer")
            return True
        
        # Connexion PostgreSQL
        print("🐘 Connexion à PostgreSQL...")
        pg_engine = create_engine(postgresql_url)
        
        # Créer la table si nécessaire
        with pg_engine.connect() as conn:
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS validation (
                    cleabs TEXT PRIMARY KEY,
                    validation TEXT,
                    commentaire TEXT DEFAULT NULL
                )
            '''))
            conn.commit()
        
        # Migration des données
        print("🔄 Migration des données...")
        df.to_sql('validation', pg_engine, if_exists='append', index=False)
        
        print("✅ Migration terminée avec succès !")
        print(f"📊 {len(df)} enregistrements migrés vers PostgreSQL")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la migration : {e}")
        return False

if __name__ == "__main__":
    print("🚀 Démarrage de la migration SQLite vers PostgreSQL")
    print("=" * 50)
    
    success = migrate_sqlite_to_postgresql()
    
    if success:
        print("=" * 50)
        print("✅ Migration terminée !")
        print("Vous pouvez maintenant utiliser PostgreSQL avec votre application.")
    else:
        print("=" * 50)
        print("❌ La migration a échoué.")
        print("Vérifiez votre configuration et réessayez.")
