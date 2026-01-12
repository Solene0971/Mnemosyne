from flask import Blueprint, render_template, request
from app.services.DonneeService import DonneeService
import sqlite3

index_bp = Blueprint('index', __name__)

@index_bp.route('/', methods=['GET', 'POST'])
def index():
    service = DonneeService()

    departements = []
    annees = []
    results = []

    db_error = False # État du système

    try:
        # On demande : Est-ce que la base est prête (tables présentes ET peuplées) ?
        if not service.is_database_ready():
            db_error = True
            print("Base de données incomplète (tables vides ou manquantes).")
        else:
            # Si la base est prête, ALORS on charge les menus
            departements = service.get_form_dept()
            annees = service.get_form_annees()

    except (sqlite3.OperationalError, Exception) as e:
        # Filet de sécurité supplémentaire (ex: fichier .db verrouillé ou corrompu)
        db_error = True
        print(f"Erreur critique d'accès BDD : {e}")

    selected_dept = "TOUS"
    selected_year = ""
    selected_rythme = "TOUS"

    if request.method == 'POST':
        selected_dept = request.form.get('departement') 
        selected_year = request.form.get('annee')
        selected_rythme = request.form.get('rythme')

    try:
        results = service.get_search_results(selected_year, selected_dept, selected_rythme)
    except Exception:
        results = []

    # On passe une liste d'objets au template
    return render_template('index.html', 
                           depts=departements,
                           annees=annees, 
                           results=results, 
                           sel_dept=selected_dept, 
                           sel_year=selected_year,
                           sel_rythme=selected_rythme,
                           db_error=db_error)