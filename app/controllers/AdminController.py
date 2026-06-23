from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from app.services.ScoDocService import ScoDocService
from app.services.DonneeService import DonneeService
from app.tools import reqlogged
from app.services.RegleService import RegleService
from app.services.UserService import UserService

# Création du Blueprint
admin_bp = Blueprint('admin', __name__)
#Création de l'objet AdminController
rs = RegleService()
us = UserService()

@admin_bp.route('/admin', methods=['GET'])
@reqlogged
def admin_dashboard():
    """Affiche la page d'administration"""
    r = rs.get_regles()
    username = session['username']
    u = us.getAllUser()
    
    return render_template('admin.html', rules = r, user = username, users = u)

@admin_bp.route('/admin/init', methods=['POST'])
@reqlogged
def initialisation():
    """Lance l'initialisation de la BDD (Action du formulaire 1)"""
    dao = DonneeService()
    msg_db = None

    try:
        dao.creation_db()
        msg_db = "Base de données initialisée avec succès."
        print("lancement")
    except Exception as e:
        msg_db = f"Erreur lors de l'initialisation : {e}"

    return render_template("admin.html", msg_db=msg_db)

@admin_bp.route('/admin/sync', methods=['POST'])
@reqlogged
def synchronisation():
    """Lance la synchronisation JSON (Action du formulaire 2)"""
    stats = None
    msg_err_import = None

    try:
        service = ScoDocService() # fonctinne parfaitement
        stats = service.run_synchronisation() #bug
    except Exception as e:
        msg_err_import = f"{e}"

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.headers.get('Accept') == 'application/json':
        return jsonify({
            'stats': stats,
            'error': msg_err_import,
        })

    r = rs.get_regles()
    return render_template('admin.html', msg_err_import=msg_err_import, stats=stats, rules=r)

@admin_bp.route('/admin/addregle', methods=['POST'])
@reqlogged
def ajouteRegle():
    nom = request.form.get('nom')
    description = request.form.get('description')
    champ = request.form.get('champ')
    operateur = request.form.get('operateur')
    valeur = request.form.get('valeur', '')

    if nom and description and champ and operateur:
        try:
            rs.ajouter_regle(nom, description, champ, operateur, valeur)
        except ValueError:
            pass

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/adduser', methods=['POST'])
@reqlogged
def ajouteUser():
    username = request.form.get('username')
    password = request.form.get('password')

    if username and password:
        us.addUser(username,password)

    
    
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/delregle', methods=['POST'])
@reqlogged
def suppRegle():
    index = int(request.form.get('index'))
    rs.supprimer_regle(index)
    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/admin/deluser', methods=['POST'])
@reqlogged
def suppUser():
    username = request.form.get('username')
    if username:
        us.delUser(username)
    return redirect(url_for('admin.admin_dashboard'))


@admin_bp.route('/admin/update_statut', methods=['POST'])
@reqlogged
def update_statut():

    index = int(request.form.get("index"))

    # Si la checkbox existe dans le form → True, sinon False
    statut = "statut" in request.form

    rs.modifier_statut(index, statut)

    return redirect(url_for('admin.admin_dashboard'))