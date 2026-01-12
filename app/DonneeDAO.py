import sqlite3
from flask import g, current_app

class DonneeDAO:
    def __init__(self):
        pass

    def get_db(self):
        """Récupère la connexion à la base stockée dans g"""
        db = getattr(g, '_database', None)
        if db is None:
            # On utilise le chemin défini dans la config de l'app
            db = g._database = sqlite3.connect(current_app.config['DATABASE'])
            db.row_factory = sqlite3.Row
        return db

    def check_data_integrity(self):
        """
        Vérifie si la base contient suffisamment de données pour fonctionner.
        Retourne True si OK, False sinon.
        """
        db = self.get_db()
        cursor = db.cursor()
        
        try:
            # 1. Vérifions les départements
            cursor.execute("SELECT COUNT(*) FROM departement")
            nb_depts = cursor.fetchone()[0]
            
            # 2. Vérifions les inscriptions (le cœur du système)
            cursor.execute("SELECT COUNT(*) FROM inscription")
            nb_inscriptions = cursor.fetchone()[0]

            # On considère que la BDD est valide s'il y a au moins 
            # 1 département ET 1 inscription
            return nb_depts > 0 and nb_inscriptions > 0
            
        except sqlite3.OperationalError:
            # Si une table n'existe pas, c'est que la BDD est cassée
            return False

    def get_all_departements(self):
        """Récupère la liste des acronymes de département"""
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT acronyme FROM departement WHERE acronyme NOT IN ('FC', 'P_CJ_GEA') ORDER BY acronyme")
        return [row['acronyme'] for row in cursor.fetchall()]

    def get_all_annees(self):
        """Récupère la liste des acronymes de département"""
        db = self.get_db()
        cursor = db.cursor()
        cursor.execute("SELECT DISTINCT annee_universitaire FROM inscription ORDER BY annee_universitaire")
        return [str(row['annee_universitaire']) for row in cursor.fetchall()]

    def search_etudiants(self, annee_debut, dept, rythme):
        """Recherche dynamique selon les critères"""
        db = self.get_db()
        cursor = db.cursor()

        params = [annee_debut]
        sql_conditions = "WHERE i.annee_universitaire = ? + (f.annee_but - 1)"

        if dept != "TOUS":
            sql_conditions += " AND d.acronyme = ?"
            params.append(dept)
        
        if rythme != "TOUS":
            if rythme == "FI":
                sql_conditions += " AND f.id_rythme = 1"
            elif rythme == "FA":
                sql_conditions += " AND f.id_rythme = 2"

        query = f"""
        SELECT 
            e.ine,
            i.annee_universitaire,
            f.annee_but,
            dec.acronyme as resultat,
            d.acronyme as dept,
            r.acronyme as rythme
        FROM inscription i
        JOIN formation f ON i.id_formation = f.id_formation
        JOIN departement d ON f.id_departement = d.id_departement
        JOIN etudiant e ON i.id_etudiant = e.id_etudiant
        JOIN rythme r ON f.id_rythme = r.id_rythme
        LEFT JOIN decision dec ON i.id_decision = dec.id_decision
        {sql_conditions}
        ORDER BY e.ine;
        """
        
        cursor.execute(query, params)
        return cursor.fetchall()
    
    def init_db(self):
        """Exécute le script schema.sql"""
        db = self.get_db()
        with current_app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()