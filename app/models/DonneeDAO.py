import sqlite3
from flask import g, current_app

CODES_ADMIS = {'ADM', 'ADM-INC', 'CMP', 'VCC'}
CODES_AJOURN = {'AJ'}
CODES_ABAN = {'ABAN', 'ATJ'}
CODES_DIPLOME = {'ADM', 'ADM-INC', 'CMP', 'VCC', 'DIP'}


def _calculate_sankey_stats(etudiants, annee_int):
    stats = {
        'but1_total': 0, 'but1_admis': 0, 'but1_redouble': 0, 'but1_abandon': 0,
        'but2_total': 0, 'but2_admis': 0, 'but2_redouble': 0, 'but2_abandon': 0,
        'but2_reorientation': 0,
        'but3_total': 0, 'but3_diplome': 0, 'but3_redouble': 0, 'but3_abandon': 0,
        'nouveaux_but2': 0,
        'redoublants_entrant_but1': 0, 'redoublants_entrant_but2': 0,
        'redoublants_entrant_but3': 0
    }

    annee0 = annee_int - 1
    annee1 = annee_int
    annee2 = annee_int + 1
    annee3 = annee_int + 2

    for etu_id, parcours in etudiants.items():
        # Redoublants entrants : mêmes BUT deux années consécutives
        if annee0 in parcours and annee1 in parcours:
            if parcours[annee0]['annee_but'] == 1 and parcours[annee1]['annee_but'] == 1:
                stats['redoublants_entrant_but1'] += 1
            if parcours[annee0]['annee_but'] == 2 and parcours[annee1]['annee_but'] == 2:
                stats['redoublants_entrant_but2'] += 1
            if parcours[annee0]['annee_but'] == 3 and parcours[annee1]['annee_but'] == 3:
                stats['redoublants_entrant_but3'] += 1

        # BUT1
        if annee1 in parcours and parcours[annee1]['annee_but'] == 1:
            stats['but1_total'] += 1
            res = parcours[annee1]['resultat']
            if annee2 in parcours and parcours[annee2]['annee_but'] == 2:
                stats['but1_admis'] += 1
            elif annee2 in parcours and parcours[annee2]['annee_but'] == 1:
                stats['but1_redouble'] += 1
            elif res in CODES_ADMIS:
                stats['but1_admis'] += 1
            else:
                stats['but1_abandon'] += 1

        # Entrées directes BUT2
        if annee1 in parcours and parcours[annee1]['annee_but'] == 2:
            stats['nouveaux_but2'] += 1

        # BUT2
        if annee2 in parcours and parcours[annee2]['annee_but'] == 2:
            stats['but2_total'] += 1
            res = parcours[annee2]['resultat']
            if annee3 in parcours and parcours[annee3]['annee_but'] == 3:
                stats['but2_admis'] += 1
            elif annee3 in parcours and parcours[annee3]['annee_but'] == 2:
                stats['but2_redouble'] += 1
            elif res in CODES_ADMIS:
                stats['but2_admis'] += 1
            elif res in CODES_AJOURN | CODES_ABAN:
                stats['but2_abandon'] += 1
            else:
                stats['but2_reorientation'] += 1

        # BUT3
        if annee3 in parcours and parcours[annee3]['annee_but'] == 3:
            stats['but3_total'] += 1
            res = parcours[annee3]['resultat']
            if res in CODES_DIPLOME:
                stats['but3_diplome'] += 1
            elif res in CODES_AJOURN:
                stats['but3_redouble'] += 1
            else:
                stats['but3_abandon'] += 1

    return stats


class DonneeDAO:
    def __init__(self):
        pass

    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(current_app.config['DATABASE'])
            db.row_factory = sqlite3.Row
        return db

    def check_data_integrity(self):
        db = self.get_db()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM departement")
            d = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM inscription")
            i = cursor.fetchone()[0]
            return d > 0 and i > 0
        except:
            return False

    def _init_db(self):
        db = self.get_db()
        with current_app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

    def get_champs_list(self):
        try:
            cur = self.get_db().cursor()

            cur.execute("SELECT acronyme, nom FROM departement ORDER BY acronyme")
            depts = [{"val": r["acronyme"], "label": f"{r['acronyme']} — {r['nom']}"} for r in cur.fetchall()]

            cur.execute("SELECT acronyme, nom FROM rythme ORDER BY acronyme")
            rythmes = [{"val": r["acronyme"], "label": f"{r['acronyme']} — {r['nom']}"} for r in cur.fetchall()]

            cur.execute("SELECT acronyme, nom FROM decision ORDER BY acronyme")
            decisions = [{"val": r["acronyme"], "label": f"{r['acronyme']} — {r['nom']}"} for r in cur.fetchall()]

            cur.execute("SELECT acronyme, nom FROM etat ORDER BY acronyme")
            etats = [{"val": r["acronyme"], "label": f"{r['acronyme']} — {r['nom']}"} for r in cur.fetchall()]

            cur.execute("SELECT DISTINCT annee_but FROM formation ORDER BY annee_but")
            annees_but = [{"val": str(r["annee_but"]), "label": f"BUT {r['annee_but']}"} for r in cur.fetchall()]
        except Exception:
            depts = rythmes = decisions = etats = []
            annees_but = []

        if not annees_but:
            annees_but = [{"val": "1", "label": "BUT 1"}, {"val": "2", "label": "BUT 2"}, {"val": "3", "label": "BUT 3"}]

        return [
            {
                "alias": "f.annee_but", "label": "Année BUT",
                "hint": "1, 2 ou 3", "placeholder": "Ex : 1",
                "ops": ["=", "!=", ">", "<", ">=", "<="],
                "values": annees_but
            },
            {
                "alias": "i.annee_universitaire", "label": "Année universitaire",
                "hint": "ex. 2021, 2022, 2023 …", "placeholder": "Ex : 2021",
                "ops": ["=", "!=", ">", "<", ">=", "<="],
                "values": None
            },
            {
                "alias": "i.moyenne", "label": "Moyenne de l'étudiant",
                "hint": "0 à 20  (ex. 10, 12.5)", "placeholder": "Ex : 10",
                "ops": ["=", "!=", ">", "<", ">=", "<="],
                "values": None
            },
            {
                "alias": "d.acronyme", "label": "Département",
                "hint": " · ".join(d["val"] for d in depts) or "CJ · GEA · INFO …",
                "placeholder": "Ex : INFO",
                "ops": ["=", "!="],
                "values": depts or None
            },
            {
                "alias": "r.acronyme", "label": "Rythme",
                "hint": "  ou  ".join(r["val"] for r in rythmes) or "FI ou FA",
                "placeholder": "Ex : FI",
                "ops": ["=", "!="],
                "values": rythmes or None
            },
            {
                "alias": "dec.acronyme", "label": "Décision du jury",
                "hint": " · ".join(d["val"] for d in decisions[:6]) + (" …" if len(decisions) > 6 else ""),
                "placeholder": "Ex : ADM",
                "ops": ["=", "!="],
                "values": decisions or None
            },
            {
                "alias": "dec.nom", "label": "Libellé décision",
                "hint": "Utilisez % comme joker avec LIKE (ex : %Admis%)",
                "placeholder": "Ex : Admis",
                "ops": ["=", "!=", "LIKE"],
                "values": None
            },
            {
                "alias": "et.acronyme", "label": "État de l'étudiant",
                "hint": "  ou  ".join(e["val"] for e in etats) or "I ou D",
                "placeholder": "Ex : I",
                "ops": ["=", "!="],
                "values": etats or None
            },
        ]

    def get_all_departements(self):
        cursor = self.get_db().cursor()
        cursor.execute("SELECT acronyme FROM departement WHERE acronyme NOT IN ('FC', 'P_CJ_GEA') ORDER BY acronyme")
        return [row['acronyme'] for row in cursor.fetchall()]

    def get_all_annees(self):
        cursor = self.get_db().cursor()
        cursor.execute("SELECT DISTINCT annee_universitaire FROM inscription ORDER BY annee_universitaire")
        return [str(row['annee_universitaire']) for row in cursor.fetchall()]

    def search_etudiants(self, annee_debut, dept, rythme, regles_sql, regles_params):
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

        if regles_sql:
            query = f"""
            SELECT DISTINCT
                e.id_etudiant,
                e.ine,
                i.annee_universitaire,
                f.annee_but,
                dec.acronyme as resultat,
                d.acronyme as dept,
                r.acronyme as rythme,
                et.acronyme as etat
            FROM etudiant e
            JOIN inscription i ON e.id_etudiant = i.id_etudiant
            JOIN formation f ON i.id_formation = f.id_formation
            JOIN departement d ON f.id_departement = d.id_departement
            LEFT JOIN decision dec ON i.id_decision = dec.id_decision
            JOIN rythme r ON f.id_rythme = r.id_rythme
            JOIN etat et ON i.id_etat = et.id_etat
            {sql_conditions} AND {regles_sql}
            ORDER BY e.ine;
            """
            cursor.execute(query, params + regles_params)
        else:
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

    def get_sankey_data(self, annee_debut, dept, rythme, regles_sql, regles_params):
        db = self.get_db()
        cursor = db.cursor()

        dept_params = []
        sql_dept = ""
        sql_rythme = ""

        if dept != "TOUS":
            sql_dept = " AND d.acronyme = ?"
            dept_params.append(dept)

        if rythme != "TOUS":
            if rythme == "FI":
                sql_rythme = " AND f.id_rythme = 1"
            elif rythme == "FA":
                sql_rythme = " AND f.id_rythme = 2"

        annee_int = int(annee_debut)

        if regles_sql:
            query = f"""
            SELECT DISTINCT
                e.id_etudiant,
                i.annee_universitaire,
                f.annee_but,
                dec.acronyme as resultat
            FROM etudiant e
            JOIN inscription i ON e.id_etudiant = i.id_etudiant
            JOIN formation f ON i.id_formation = f.id_formation
            JOIN departement d ON f.id_departement = d.id_departement
            LEFT JOIN decision dec ON i.id_decision = dec.id_decision
            JOIN rythme r ON f.id_rythme = r.id_rythme
            JOIN etat et ON i.id_etat = et.id_etat
            WHERE {regles_sql} AND i.annee_universitaire BETWEEN ? AND ?
            {sql_dept}
            {sql_rythme}
            ORDER BY e.id_etudiant, i.annee_universitaire
            """
            all_params = regles_params + [annee_int - 1, annee_int + 2] + dept_params
        else:
            query = f"""
            SELECT
                e.id_etudiant,
                i.annee_universitaire,
                f.annee_but,
                dec.acronyme as resultat
            FROM etudiant e
            JOIN inscription i ON e.id_etudiant = i.id_etudiant
            JOIN formation f ON i.id_formation = f.id_formation
            JOIN departement d ON f.id_departement = d.id_departement
            LEFT JOIN decision dec ON i.id_decision = dec.id_decision
            WHERE i.annee_universitaire BETWEEN ? AND ?
            {sql_dept}
            {sql_rythme}
            ORDER BY e.id_etudiant, i.annee_universitaire
            """
            all_params = [annee_int - 1, annee_int + 2] + dept_params

        cursor.execute(query, all_params)
        rows = cursor.fetchall()

        etudiants = {}
        for row in rows:
            etu_id = row['id_etudiant']
            if etu_id not in etudiants:
                etudiants[etu_id] = {}
            etudiants[etu_id][row['annee_universitaire']] = {
                'annee_but': row['annee_but'],
                'resultat': row['resultat']
            }

        return _calculate_sankey_stats(etudiants, annee_int)
