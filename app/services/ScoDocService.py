# [file name]: ScoDocService.py
from app.ScoDocAPI import ScoDocAPI
from app.DonneeDAO import DonneeDAO
from flask import current_app
import os
from typing import Dict, List, Optional

class ScoDocService:
    """Service pour gérer la synchronisation avec ScoDoc"""
    
    def __init__(self):
        self.dao = DonneeDAO()
        
        # Configuration depuis les variables d'environnement
        sco_doc_url = os.environ.get('SCODOC_URL', 'https://scodoc.univ-paris13.fr')
        sco_doc_token = os.environ.get('SCODOC_API_TOKEN', '')
        
        if not sco_doc_token:
            current_app.logger.warning("Token API ScoDoc non configuré")
        
        self.api = ScoDocAPI(sco_doc_url, sco_doc_token)

    def get_donnees_etudiant(self, ine: str) -> Optional[Dict]:
        """Récupère les données complètes d'un étudiant depuis ScoDoc"""
        return self.api.get_donnees_etudiant_completes(ine)
    
    def est_connecte(self) -> bool:
        """Vérifie si on peut se connecter à ScoDoc"""
        ok, _ = self.api.test_connexion()
        return ok
    
    def synchroniser_avec_sco_doc(self, annee_debut: int = 2021) -> Dict:
        """
        Synchronise les données avec ScoDoc et les insère en base
        
        Returns:
            Dict: Statistiques de synchronisation
        """
        stats = {
            'insertions': {
                'departements': 0,
                'rythmes': 0,
                'formations': 0,
                'etudiants': 0,
                'inscriptions': 0,
                'decisions': 0,
            },
            'erreurs': []
        }
        
        try:
            db = self.dao.get_db()
            cursor = db.cursor()
            
            # 1. Tester la connexion
            connexion_ok, message = self.api.test_connexion()
            if not connexion_ok:
                stats['erreurs'].append(f"Échec connexion: {message}")
                return stats
            
            current_app.logger.info(message)
            
            # 2. Récupérer les données de base depuis ScoDoc
            rythmes_api = self.api.get_rythmes()
            for rythme in rythmes_api:
                cursor.execute(
                    "INSERT OR IGNORE INTO rythme (id_rythme, nom, acronyme) VALUES (?, ?, ?)",
                    (rythme['id'], rythme['nom'], rythme['acronyme'])
                )
                if cursor.rowcount > 0:
                    stats['insertions']['rythmes'] += 1
            
            # Départements
            departements_api = self.api.get_departements()
            for dept in departements_api:
                cursor.execute(
                    "INSERT OR IGNORE INTO departement (id_departement, nom, acronyme) VALUES (?, ?, ?)",
                    (dept['id'], dept['nom'], dept['acronyme'])
                )
                if cursor.rowcount > 0:
                    stats['insertions']['departements'] += 1
            
            # 3. Formations
            for dept in departements_api:
                formations_api = self.api.get_formations(dept_id=dept['id'])
                for formation in formations_api:
                    # Déterminer l'année BUT
                    annee_but = self._determiner_annee_but(formation)
                    
                    cursor.execute(
                        """INSERT OR IGNORE INTO formation 
                           (acronyme, annee_but, id_departement, id_rythme) 
                           VALUES (?, ?, ?, ?)""",
                        (formation.get('acronyme', ''), 
                         annee_but,
                         dept['id'],
                         formation.get('rythme_id', 1))
                    )
                    if cursor.rowcount > 0:
                        stats['insertions']['formations'] += 1
            
            
            # 4. Étudiants et inscriptions (par formation et année)
            for dept in departements_api:
                formations_api = self.api.get_formations(dept_id=dept['id'])
                
                for formation in formations_api:
                    formation_id = formation['id']
                    
                    # Pour les dernières années
                    current_year = datetime.now().year
                    for year_offset in range(0, 4):  # 4 dernières années
                        annee = current_year - year_offset
                        annee_str = f"{annee}-{annee+1}"
                        
                        etudiants_api = self.api.get_etudiants_formation(
                            formation_id, 
                            annee_str
                        )
                        
                        for etudiant in etudiants_api: #il faut ajouter l'insertion des compétences et dans la table évaluer les notes
                            # Insertion étudiant
                            ine = etudiant.get('ine', etudiant.get('etudid', ''))
                            if ine:
                                cursor.execute(
                                    "INSERT OR IGNORE INTO etudiant (ine) VALUES (?)",
                                    (ine,)
                                )
                                if cursor.rowcount > 0:
                                    stats['insertions']['etudiants'] += 1
                            
                                # Récupérer l'ID de l'étudiant
                                cursor.execute(
                                    "SELECT id_etudiant FROM etudiant WHERE ine = ?",
                                    (ine,)
                                )
                                result = cursor.fetchone()
                                if result:
                                    etudiant_id = result[0]
                                    
                                    # Insertion inscription
                                    cursor.execute(
                                        """INSERT OR IGNORE INTO inscription 
                                           (annee_universitaire, id_etudiant, id_formation, 
                                            id_decision, id_etat) 
                                           VALUES (?, ?, ?, ?, ?)""",
                                        (annee,
                                         etudiant_id,
                                         formation_id,
                                         etudiant.get('decision_id'),  # À adapter est-ce les decision_id venant de etudiant sont les même que ceux su'on va insérer ?
                                         1)  # État par défaut: Inscrit bah nan certain ne sont plus inscrits /!\
                                    )
                                    if cursor.rowcount > 0:
                                        stats['insertions']['inscriptions'] += 1
            
            db.commit()
                        
            current_app.logger.info(f"Synchronisation terminée: {stats}")
            
        except Exception as e:
            db.rollback()
            stats['erreurs'].append(str(e))
            current_app.logger.error(f"Erreur lors de la synchronisation: {e}")
        
        return stats
    
    def _determiner_annee_but(self, formation: Dict) -> int:
        """Détermine l'année BUT à partir des données de formation"""
        acronyme = formation.get('acronyme', '').upper()
        
        if 'BUT1' in acronyme or '1A' in acronyme or '1ÈRE' in acronyme:
            return 1
        elif 'BUT2' in acronyme or '2A' in acronyme or '2ÈME' in acronyme:
            return 2
        elif 'BUT3' in acronyme or '3A' in acronyme or '3ÈME' in acronyme:
            return 3
        else:
            # Fallback: essayer de parser depuis le nom
            nom = formation.get('nom', '')
            if 'première' in nom.lower() or '1' in nom:
                return 1
            elif 'deuxième' in nom.lower() or '2' in nom:
                return 2
            elif 'troisième' in nom.lower() or '3' in nom:
                return 3
            else:
                return 1  # Par défaut
    