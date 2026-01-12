from flask import Blueprint, render_template
from app.services.DonneeService import DonneeService
from app.DonneeDAO import DonneeDAO

synchro_bp = Blueprint('synchro', __name__)


@synchro_bp.route('/setup', methods=['GET'])
def setup():
    """Route utilitaire pour créer la DB et importer les données"""

    return render_template('setup.html')

# Initialisation de la base de données
@synchro_bp.route('/setup/init', methods=['POST'])
def initialisation():
    """Lance la synchronisation avec les données JSON"""
    dao = DonneeDAO()
    service = DonneeService()

    # Création des tables apparemment fonctionne
    try:
        dao.init_db()
        msg_db = "Base de données initialisée."
    except Exception as e:
        msg_db = f"Erreur DB: {e}"

    return render_template("setup.html", msg_db=msg_db)

# Synchronisation de la base de données avec les JSON
@synchro_bp.route('/setup/sync', methods=['POST'])
def synchronisation():
    """Lance la synchronisation avec les données JSON"""
    dao = DonneeDAO()
    service = DonneeService()

    #stats d'import mais ne fonctionnent pas correctement car même les INSERT IGNORÉS sont compté comme des insertions finales
    stats = None

    # Import des données JSON
    try:
        stats = service.run_import_pipeline()
        msg_import = "Données importées depuis les JSON."
    except Exception as e:
        msg_import = f"Erreur Import: {e}"
    
    return render_template('setup.html', msg_import=msg_import, stats=stats)

