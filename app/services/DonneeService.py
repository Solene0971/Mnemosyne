import os
import json
import glob
import re
from app.models.DonneeDAO import DonneeDAO
from app.models.Etudiant import EtudiantView
from flask import current_app

class DonneeService:
    def __init__(self):
        self.dao = DonneeDAO()

    def creation_db(self):
        self.dao._init_db()

    def is_database_ready(self):
        return self.dao.check_data_integrity()

    def get_form_dept(self):
        return self.dao.get_all_departements()

    def get_form_annees(self):
        return self.dao.get_all_annees()

    def get_search_results(self, year, dept, rythme, regles_sql, regles_params=None):
        if not year:
            return []
        try:
            annee_int = int(year)
            rows = self.dao.search_etudiants(annee_int, dept, rythme, regles_sql, regles_params or [])
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

    def get_champs_list(self):
        return self.dao.get_champs_list()

    def get_sankey_stats(self, year, dept, rythme, regles_sql, regles_params=None):
        if not year:
            return None
        try:
            return self.dao.get_sankey_data(year, dept, rythme, regles_sql, regles_params or [])
        except Exception as e:
            print(f"Erreur calcul Sankey : {e}")
            return None
