#!/usr/bin/env python3
"""
Script de test pour vérifier la connexion à la base de données

Usage: 
    source venv/bin/activate
    python test_database.py
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def test_database_connection():
    """Teste la connexion à la base de données"""
    
    # Charger les variables d'environnement
    load_dotenv()
    
    database_url = os.getenv('DATABASE_URL', 'sqlite:///resultats_batiments.sqlite')
    
    # Correction pour les URLs PostgreSQL avec le dialecte 'postgres'
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    print(f"🔍 Test de connexion à : {database_url.split('@')[0] + '@***' if '@' in database_url else database_url}")
    
    try:
        # Créer le moteur
        engine = create_engine(database_url)
        
        # Tester la connexion
        with engine.connect() as conn:
            # Créer la table de test
            conn.execute(text('''
                CREATE TABLE IF NOT EXISTS validation (
                    cleabs TEXT PRIMARY KEY,
                    validation TEXT,
                    commentaire TEXT DEFAULT NULL
                )
            '''))
            conn.commit()
            
            # Compter les enregistrements
            result = conn.execute(text("SELECT COUNT(*) FROM validation"))
            count = result.fetchone()[0]
            
            print(f"✅ Connexion réussie !")
            print(f"📊 {count} enregistrement(s) dans la table 'validation'")
            
            # Tester l'écriture
            test_cleabs = "TEST_CONNEXION"
            conn.execute(text('''
                INSERT INTO validation (cleabs, validation, commentaire)
                VALUES (:cleabs, :validation, :commentaire)
                ON CONFLICT(cleabs) DO UPDATE SET 
                    validation = EXCLUDED.validation, 
                    commentaire = EXCLUDED.commentaire
            '''), {"cleabs": test_cleabs, "validation": "Test", "commentaire": "Test de connexion"})
            conn.commit()
            
            # Supprimer le test
            conn.execute(text("DELETE FROM validation WHERE cleabs = :cleabs"), {"cleabs": test_cleabs})
            conn.commit()
            
            print("✅ Test d'écriture/lecture réussi !")
            
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False

if __name__ == "__main__":
    print("🧪 Test de connexion à la base de données")
    print("=" * 40)
    
    success = test_database_connection()
    
    print("=" * 40)
    if success:
        print("✅ Tous les tests sont passés !")
    else:
        print("❌ Échec des tests. Vérifiez votre configuration.")
