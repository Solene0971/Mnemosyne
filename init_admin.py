import sqlite3
import bcrypt
import os
from dotenv import load_dotenv


def _generatePwdHash(password):
    """Génère un hash bcrypt pour un mot de passe."""
    password_bytes = password.encode('utf-8')
    hashed_bytes = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


def create_admin_db():
    """
    Crée la base de données admin et l'utilisateur admin si nécessaire.
    Vérifie que :
    - la DB n'existe pas
    - la DB existe mais pas d'admin
    - la DB et admin existent
    """
    load_dotenv()

    # Configuration des chemins
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    DB_PATH = os.path.join(INSTANCE_DIR, 'database.db')
    SCHEMA_PATH = os.path.join(BASE_DIR, 'app', 'schema_admin.sql')

    # Création du dossier instance s'il n'existe pas
    if not os.path.exists(INSTANCE_DIR):
        os.makedirs(INSTANCE_DIR)
        print(f"Dossier créé : {INSTANCE_DIR}")

    # Récupérer les informations admin
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
    admin_pwd_hash = _generatePwdHash(admin_password)

    # Vérifier si la DB existe
    db_exists = os.path.exists(DB_PATH)

    # Connexion à la base de données
    print(f"Connexion à la base de données : {DB_PATH}")
    connection = sqlite3.connect(DB_PATH)
    cur = connection.cursor()

    # Si la DB n'existe pas, exécuter le schéma
    if not db_exists:
        print(f"Exécution du schéma SQL : {SCHEMA_PATH}")
        with open(SCHEMA_PATH, 'r') as f:
            connection.executescript(f.read())
        connection.commit()
        print("BD créée.")

    # Vérifier si l'admin existe
    cur.execute("SELECT id FROM admin WHERE username = ?", (admin_username,))
    admin_exists = cur.fetchone() is not None

    # Si l'admin n'existe pas, le créer
    if not admin_exists:
        try:
            cur.execute("INSERT INTO admin (username, password) VALUES (?, ?)", 
                       (admin_username, admin_pwd_hash))
            connection.commit()
            print(f"Utilisateur admin '{admin_username}' créé.")
        except sqlite3.Error as e:
            print(f"Erreur lors de la création de l'admin : {e}")
            connection.close()
            return False

    connection.close()
    return True


if __name__ == '__main__':
    create_admin_db()