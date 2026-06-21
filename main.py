from app import create_app
import os
from dotenv import load_dotenv
from init_admin import create_admin_db

# Charger les variables du fichier .env
load_dotenv()

# Initialiser la base de données admin
create_admin_db()

app = create_app()

if __name__ == '__main__':
    app.run(host=os.getenv("HOST"), port=os.getenv("PORT"), debug=os.getenv("FLASK_DEBUG"))