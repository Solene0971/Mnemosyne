import os
from flask import Flask, g

def create_app():
    # Configuration des chemins
    # BASE_DIR est le dossier 'app'
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    # Le dossier parent contient 'instance'
    INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
    # Config BDD
    DB_PATH = os.path.join(INSTANCE_DIR, 'scolarite.db')
    
    app = Flask(__name__, instance_path=INSTANCE_DIR)
    app.config['DATABASE'] = DB_PATH

    # S'assurer que le dossier instance existe
    try:
        os.makedirs(os.path.dirname(DB_PATH))
    except OSError:
        pass

    # Enregistrement des Blueprints (Contrôleurs)
    from app.controllers.IndexController import index_bp
    from app.controllers.SynchroController import synchro_bp
    
    app.register_blueprint(index_bp)
    app.register_blueprint(synchro_bp)

    # Gestion fermeture connexion DB
    @app.teardown_appcontext
    def close_connection(exception):
        db = getattr(g, '_database', None)
        if db is not None:
            db.close()

    return app