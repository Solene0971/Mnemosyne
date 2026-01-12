import os
import json
import glob
import re
from app.DonneeDAO import DonneeDAO
from app.Etudiant import EtudiantView
from flask import current_app

class DonneeService:
    def __init__(self):
        self.dao = DonneeDAO()

    def is_database_ready(self):
        """Demande au DAO si les données sont cohérentes"""
        return self.dao.check_data_integrity()

    def get_form_dept(self):
        """Retourne les options de département pour le formulaire"""
        return self.dao.get_all_departements()

    def get_form_annees(self):
        """Retourne les options d'années pour le formulaire"""
        return self.dao.get_all_annees()    

    def get_search_results(self, year, dept, rythme):
        """Retourne les objets EtudiantView après recherche"""
        if not year:
            return []
        
        try:
            annee_int = int(year)
            rows = self.dao.search_etudiants(annee_int, dept, rythme)
            # Transformation des lignes SQL en objets métier
            return [
                EtudiantView(
                    ine=row['ine'], 
                    annee_univ=row['annee_universitaire'], 
                    annee_but=row['annee_but'], 
                    resultat=row['resultat'], 
                    dept=row['dept'], 
                    rythme=row['rythme']
                ) for row in rows
            ]
        except ValueError:
            return []

    def run_import_pipeline(self):
        """
        Logique massive d'importation (ancien import_data.py)
        pour utiliser le DAO
        """
        db = self.dao.get_db()
        cursor = db.cursor()
        
        #CETTE PARTIE LÀ SERA PROBABKEMENT À MODIFIER POUR Y AJOUTER UNE FONCTION QUI LANCE UNE CONNECTION À L'API SCODOC ET RÉCUPÈRE LES DONNÉES
        # Chemins vers les fichiers 
        json_dir = os.path.join(current_app.static_folder, 'data', 'json')
        print(f"Import depuis : {json_dir}")

        # 1. Chargement des fichiers JSON
        try:
            with open(os.path.join(json_dir, 'departements.json'), 'r', encoding='utf-8') as f:
                depts_json = json.load(f)

        except FileNotFoundError:
            print("Fichiers de configuration manquants.")
            return

        # Fonctions internes d'import 
        self._import_decisions(cursor)
        self._import_departements(cursor, depts_json)
        self._import_rythmes(cursor)
        self._import_etats(cursor)
        self._import_etudiants(cursor, json_dir)
        self._import_formations(cursor)
        self._import_inscriptions(cursor, json_dir)

        total_etu, nouveaux_etu = self._import_etudiants(cursor, json_dir)
        
        self._import_formations(cursor)
        nb_inscriptions = self._import_inscriptions(cursor, json_dir)

        db.commit()
        print("Import terminé avec succès.")  #retirer les print on s'en sert pas nan ?

        # On calcule ceux déjà présents
        deja_connus = total_etu - nouveaux_etu

        # On retourne un dictionnaire de résultats
        return {
            "total_distincts": total_etu,
            "nouveaux": nouveaux_etu,
            "connus": deja_connus,
            "inscriptions": nb_inscriptions
        }

    # Méthodes privées d'import

    def _import_decisions(self, cursor):
        codes = [
            ("Admis", "ADM"), ("Ajourné", "AJ"), ("Admis par Compensation", "CMP"),
            ("Admis Supérieur", "ADSUP"), ("Ajourné (Rattrapage)", "ADJR"),
            ("Ajourné (Jury)", "ADJ"), ("Défaillant", "DEF"), ("Non Admis Redouble", "NAR"),
            ("Redoublement", "RED"), ("Passage de Droit", "PASD"), 
            ("Passage Conditionnel", "PAS1NCI"), ("En attente", "ATT"),
            ("En attente (Bloqué)", "ATB"), ("Validé", "V"), ("Validé (Variante)", "VAL"),
            ("Non Validé", "NV"), ("Validé par Compensation Annuelle", "VCA"),
            ("Validé par Commission", "VCC"), ("Admis Sous Réserve", "ADM-INC"),
            ("Démissionnaire", "DEM"), ("Absence Injustifiée", "ABI"),
            ("Absence Justifiée", "ABJ"), ("Excusé", "EXC"), ("Non Inscrit", "NI"),
            ("Année Blanche", "ABL"), ("Inscrit (En cours)", "INS"), 
            ("Abdandon", "ABAN"), ("Attente Jury", "ATJ")
        ]
        cursor.executemany("INSERT OR IGNORE INTO decision (nom, acronyme) VALUES (?, ?)", codes)

    def _import_departements(self, cursor, data):
        donnees = [(d['id'], d['dept_name'], d['acronym']) for d in data]
        donnees.append((9, "Passerelle SD INFO", "P_SD_INFO"))
        donnees.append((10, "Passerelle CJ GEA", "P_CJ_GEA"))
        cursor.executemany("INSERT OR REPLACE INTO departement (id_departement, nom, acronyme) VALUES (?, ?, ?)", donnees)

    def _import_rythmes(self, cursor):
        cursor.execute("INSERT OR REPLACE INTO rythme (id_rythme, nom, acronyme) VALUES (1, 'Formation Initiale', 'FI')")
        cursor.execute("INSERT OR REPLACE INTO rythme (id_rythme, nom, acronyme) VALUES (2, 'Formation Apprentissage', 'FA')")

    def _import_etats(self, cursor):
        cursor.execute("INSERT OR REPLACE INTO etat (id_etat, nom, acronyme) VALUES (1, 'Inscrit', 'I')")
        cursor.execute("INSERT OR REPLACE INTO etat (id_etat, nom, acronyme) VALUES (2, 'Démission', 'D')")

# séparer l'import manuel des décisions etc. qui ne vont pas changer avec 
# l'import des étudiants/formations/inscriptions qui se synchronysent
    def _import_etudiants(self, cursor, dossier_json):
        files = glob.glob(os.path.join(dossier_json, "decisions_*.json"))
        ines = set()
        for f_path in files:
            try:
                with open(f_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    for rec in content:
                        ine = rec.get('etudid')
                        if ine: ines.add(ine)
            except Exception: pass
        cursor.executemany("INSERT OR IGNORE INTO etudiant (ine) VALUES (?)", [(ine,) for ine in ines])

        nb_ajoutes = cursor.rowcount
        nb_total = len(ines)
        
        return nb_total, nb_ajoutes

    def _import_formations(self, cursor):
        # Logique identique à ton script
        annee_alternance = {2: 1, 1: 3, 3: 2, 4: 2, 5: 2, 8: 2} # GEA, CJ, GEII, INFO, RT, SD
        cursor.execute("SELECT id_departement FROM departement")
        all_depts = [r[0] for r in cursor.fetchall()]
        to_insert = []
        for d_id in all_depts:
            if d_id not in [9, 10]:
                for a in [1, 2, 3]: to_insert.append((a, d_id, 1)) # FI
                if d_id in annee_alternance:
                    debut_fa = annee_alternance[d_id]
                    for a in [1, 2, 3]:
                        if a >= debut_fa: to_insert.append((a, d_id, 2)) # FA
        if 9 in all_depts: to_insert.append((2, 9, 1))
        if 10 in all_depts: to_insert.append((2, 10, 1))
        cursor.executemany("INSERT OR IGNORE INTO formation (annee_but, id_departement, id_rythme) VALUES (?, ?, ?)", to_insert)

    def _import_inscriptions(self, cursor, dossier_json):
        # Cache création
        cursor.execute("SELECT acronyme, id_departement FROM departement")
        cache_depts = {r[0].upper(): r[1] for r in cursor.fetchall()}
        cursor.execute("SELECT ine, id_etudiant FROM etudiant")
        cache_etus = {r[0].strip().lower(): r[1] for r in cursor.fetchall()}
        cursor.execute("SELECT acronyme, id_decision FROM decision")
        cache_dec = {r[0].upper(): r[1] for r in cursor.fetchall()}
        cursor.execute("SELECT id_departement, annee_but, id_rythme, id_formation FROM formation")
        cache_form = {(r[0], r[1], r[2]): r[3] for r in cursor.fetchall()}

        files = glob.glob(os.path.join(dossier_json, "decisions_*.json"))
        inscriptions = []

        for f_path in files:
            fname = os.path.basename(f_path)
            id_dept = self._get_dept_id_from_name(fname, cache_depts)
            if not id_dept: continue

            annee_match = re.search(r'(\d{4})', fname)
            annee_fic = int(annee_match.group(1)) if annee_match else None
            
            # Rythme de formation
            is_fa = any(x in fname.lower() for x in ['fa', 'apprentissage', 'alternance', 'alt'])
            id_rythme_fic = 2 if is_fa else 1

            try:
                with open(f_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
            except: continue

            liste = content if isinstance(content, list) else content.get('etudiants', [])

            for etu in liste:
                ine = etu.get('etudid')
                if not ine: continue
                id_etudiant = cache_etus.get(str(ine).strip().lower())
                if not id_etudiant: continue

                # Decision extraction
                dec_data = etu.get('decision', {}) if isinstance(etu.get('decision'), dict) else {}
                ann_data = etu.get('annee', {}) if isinstance(etu.get('annee'), dict) else {}
                sem_data = etu.get('semestre', {}) if isinstance(etu.get('semestre'), dict) else {}

                c_dec = ann_data.get('code') or dec_data.get('code') or sem_data.get('code')
                
                # Fallback etats
                etat_adm = etu.get('etat')
                if not c_dec:
                    if etat_adm == 'D': c_dec = 'DEM'
                    elif etat_adm == 'DEF': c_dec = 'DEF'
                    elif etat_adm == 'ABAN': c_dec = 'DEM'
                    elif etat_adm == 'I': c_dec = 'INS'
                
                if not c_dec: continue

                annee_reelle = annee_fic
                if ann_data.get('annee_scolaire'):
                    try: annee_reelle = int(ann_data.get('annee_scolaire'))
                    except: pass
                
                if not annee_reelle: continue

                id_decision = cache_dec.get(str(c_dec).upper())
                
                # Niveau / Formation
                niveau = 1
                ordre = str(ann_data.get('ordre', '')).upper()
                if '3' in ordre: niveau = 3
                elif '2' in ordre: niveau = 2
                
                # Passerelles
                if id_dept in [cache_depts.get('P_SD_INFO'), cache_depts.get('P_CJ_GEA')]:
                     id_form = cache_form.get((id_dept, 2, id_rythme_fic))
                else:
                    id_form = cache_form.get((id_dept, niveau, id_rythme_fic))

                # FA
                if not id_form and id_rythme_fic == 2:
                    id_form = cache_form.get((id_dept, 2, 2)) or cache_form.get((id_dept, 3, 2))
                
                if not id_form: continue

                id_etat = 2 if c_dec in ['DEM', 'DEF', 'ABAN', 'NI', 'D'] else 1
                inscriptions.append((annee_reelle, id_etudiant, id_etat, id_form, id_decision))

        cursor.executemany("INSERT OR IGNORE INTO inscription (annee_universitaire, id_etudiant, id_etat, id_formation, id_decision) VALUES (?, ?, ?, ?, ?)", inscriptions)
        # On retourne le nombre d'inscriptions ajoutées
        return cursor.rowcount


    def _get_dept_id_from_name(self, name, cache):
        name = name.lower()
        if "passerelle" in name:
            if any(x in name for x in ["sd", "info"]): return cache.get('P_SD_INFO')
            if any(x in name for x in ["cj", "gea"]): return cache.get('P_CJ_GEA')
            return None
        if any(x in name for x in ["geii", "electrique"]): return cache.get('GEII')
        if any(x in name for x in ["rt", "reseaux"]): return cache.get('RT')
        if any(x in name for x in ["stid", "donn"]): return cache.get('STID')
        if any(x in name for x in ["info", "informatique"]): return cache.get('INFO')
        if any(x in name for x in ["cj", "juridique"]): return cache.get('CJ')
        if "gea" in name: return cache.get('GEA')
        return None