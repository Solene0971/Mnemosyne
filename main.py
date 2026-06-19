from app import create_app
import os
from dotenv import load_dotenv

# Charger les variables du fichier .env
load_dotenv()
app = create_app()

if __name__ == '__main__':
    app.run(host=os.getenv("HOST"), port=os.getenv("PORT"), debug=os.getenv("FLASK_DEBUG"))