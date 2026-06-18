from flask import Blueprint, render_template, request, url_for
from app.services.DonneeService import DonneeService
from app.services.RegleService import RegleService
import sqlite3

index_bp = Blueprint('index', __name__)

@index_bp.route('/', methods=['GET'])
def index():
    service = DonneeService()
    departements = []
    annees = []
    db_error = False

    try:
        if not service.is_database_ready():
            db_error = True
        else:
            departements = service.get_form_dept()
            annees = service.get_form_annees()
    except Exception as e:
        db_error = True
        print(f"Erreur BDD : {e}")

    return render_template('index.html',
                           depts=departements,
                           annees=annees,
                           db_error=db_error)

@index_bp.route('/cohorte', methods=['GET', 'POST'])
def cohorte():
    service = DonneeService()
    results = []
    sankey_stats = None
    rs = RegleService()

    if request.method == 'POST':
        selected_dept = request.form.get('departement')
        selected_year = request.form.get('annee')
        selected_rythme = request.form.get('rythme')
    else:
        selected_dept = request.args.get('dept')
        selected_year = request.args.get('year')
        selected_rythme = request.args.get('rythme', 'TOUS')

    try:
        year_int = int(selected_year) if selected_year else 2021
    except:
        year_int = 2021

    try:
        regles_sql, regles_params = rs.finSQL()
        results = service.get_search_results(selected_year, selected_dept, selected_rythme, regles_sql, regles_params)
        sankey_stats = service.get_sankey_stats(selected_year, selected_dept, selected_rythme, regles_sql, regles_params)
    except Exception as e:
        print(f"Erreur recherche : {e}")
        results = []
        sankey_stats = None

    unique_students = len(set(r.ine for r in results)) if results else 0

    fi_unique_count = 0
    fa_unique_count = 0
    fi_diplome_count = 0
    fa_diplome_count = 0

    # Le graphique FI/FA n'a de sens que quand on n'a pas filtré par rythme
    if selected_rythme == 'TOUS':
        try:
            fi_results = service.get_search_results(selected_year, selected_dept, 'FI', regles_sql, regles_params)
            fi_stats = service.get_sankey_stats(selected_year, selected_dept, 'FI', regles_sql, regles_params)
            fi_unique_count = len(set(r.ine for r in fi_results)) if fi_results else 0
            fi_diplome_count = fi_stats.get('but3_diplome', 0) if fi_stats else 0

            fa_results = service.get_search_results(selected_year, selected_dept, 'FA', regles_sql, regles_params)
            fa_stats = service.get_sankey_stats(selected_year, selected_dept, 'FA', regles_sql, regles_params)
            fa_unique_count = len(set(r.ine for r in fa_results)) if fa_results else 0
            fa_diplome_count = fa_stats.get('but3_diplome', 0) if fa_stats else 0
        except Exception as e:
            print(f"Erreur calcul statistiques FI/FA : {e}")

    return render_template('cohorte.html',
                           results=results,
                           unique_count=unique_students,
                           sel_dept=selected_dept,
                           sel_year=selected_year,
                           sel_rythme=selected_rythme,
                           selected_year=year_int,
                           selected_dept=selected_dept,
                           selected_rythme=selected_rythme,
                           sankey_stats=sankey_stats,
                           fi_unique_count=fi_unique_count,
                           fi_diplome_count=fi_diplome_count,
                           fa_unique_count=fa_unique_count,
                           fa_diplome_count=fa_diplome_count)
