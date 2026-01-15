# [file name]: ScoDocAPI.py
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import time
from flask import current_app

class ScoDocAPI:
    """Classe pour interagir avec l'API ScoDoc"""
    
    def __init__(self, base_url: str, api_token: str):
        """
        Initialise la connexion à l'API ScoDoc
        
        Args:
            base_url: URL de base de l'API ScoDoc (ex: "https://scodoc.univ-paris13.fr")
            api_token: Token d'authentification API
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Bearer {api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Cache pour optimiser les requêtes
        self._departements_cache = None
        self._formations_cache = {}
        self._rythmes_cache = None
        
    def _make_request(self, endpoint: str, method: str = 'GET', 
                     params: Optional[Dict] = None, data: Optional[Dict] = None) -> Optional[Dict]:
        """
        Effectue une requête à l'API ScoDoc
        
        Returns:
            Dict or None: Réponse JSON ou None en cas d'erreur
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            else:
                response = self.session.request(method, url, json=data, params=params, timeout=30)
            
            response.raise_for_status()
            
            # Certaines APIs retournent du texte brut
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' in content_type:
                return response.json()
            else:
                # Essaye de parser comme JSON
                try:
                    return response.json()
                except:
                    return {'text': response.text}
                    
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Erreur API ScoDoc {endpoint}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                current_app.logger.error(f"Status: {e.response.status_code}")
                current_app.logger.error(f"Response: {e.response.text}")
            return None

    def test_connexion(self) -> Tuple[bool, str]:
        """Teste la connexion à l'API ScoDoc"""
        try:
            result = self._make_request("/api/v1/ping")  # Endpoint de test
            
            if result:
                return True, "Connexion à l'API ScoDoc réussie"
            else:
                return False, "Pas de réponse de l'API ScoDoc"
                
        except Exception as e:
            return False, f"Erreur de connexion: {str(e)}"
    
    # Méthodes pour récupérer les données de base
    def get_departements(self) -> List[Dict]:
        """Récupère la liste des départements"""
        if self._departements_cache is None:
            endpoint = "/api/v1/departements"  # À adapter selon votre API
            result = self._make_request(endpoint)
            if result:
                self._departements_cache = result.get('departements', [])
            else:
                self._departements_cache = []
        return self._departements_cache
    
    def get_formations(self, dept_id: Optional[int] = None, annee: Optional[int] = None) -> List[Dict]:
        """Récupère les formations d'un département"""
        cache_key = f"{dept_id}_{annee}"
        if cache_key not in self._formations_cache:
            endpoint = "/api/v1/formations"
            params = {}
            if dept_id:
                params['departement_id'] = dept_id
            if annee:
                params['annee'] = annee
                
            result = self._make_request(endpoint, params=params)
            if result:
                self._formations_cache[cache_key] = result.get('formations', [])
            else:
                self._formations_cache[cache_key] = []
        return self._formations_cache[cache_key]
    
    #on peut le retirer les rythmesil y en a que deux
    def get_rythmes(self) -> List[Dict]:
        """Récupère les types de rythme (FI/APP)"""
        if self._rythmes_cache is None:
            # Endpoint spécifique ou on peut extraire des formations
            formations = self.get_formations()
            rythmes_set = set()
            
            for formation in formations:
                if 'rythme' in formation:
                    rythmes_set.add((formation['rythme']['id'], 
                                   formation['rythme']['nom'], 
                                   formation['rythme']['acronyme']))
            
            self._rythmes_cache = [{'id': r[0], 'nom': r[1], 'acronyme': r[2]} 
                                  for r in rythmes_set]
            
            # Si pas trouvé, valeurs par défaut
            if not self._rythmes_cache:
                self._rythmes_cache = [
                    {'id': 1, 'nom': 'Formation Initiale', 'acronyme': 'FI'},
                    {'id': 2, 'nom': 'Apprentissage', 'acronyme': 'APP'}
                ]
                
        return self._rythmes_cache
    
    def get_etudiants_formation(self, formation_id: int, annee_universitaire: str) -> List[Dict]:
        """Récupère les étudiants d'une formation pour une année donnée"""
        endpoint = f"/api/v1/formations/{formation_id}/etudiants"
        params = {'annee_universitaire': annee_universitaire}
        result = self._make_request(endpoint, params=params)
        return result.get('etudiants', []) if result else []
    
    def get_inscriptions_etudiant(self, etudiant_id: int) -> List[Dict]:
        """Récupère toutes les inscriptions d'un étudiant"""
        endpoint = f"/api/v1/etudiants/{etudiant_id}/inscriptions"
        result = self._make_request(endpoint)
        return result.get('inscriptions', []) if result else []
    
    def get_decisions_etudiant(self, etudiant_id: int, formation_id: int) -> List[Dict]:
        """Récupère les décisions de jury d'un étudiant dans une formation"""
        endpoint = f"/api/v1/etudiants/{etudiant_id}/formations/{formation_id}/decisions"
        result = self._make_request(endpoint)
        return result.get('decisions', []) if result else []
    
    def get_competences_etudiant(self, etudiant_id: int, formation_id: int) -> List[Dict]:
        """Récupère les compétences évaluées d'un étudiant"""
        endpoint = f"/api/v1/etudiants/{etudiant_id}/formations/{formation_id}/competences"
        result = self._make_request(endpoint)
        return result.get('competences', []) if result else []
 

    # Méthodes de synchronisation complète
    #j'ai ajouté la synchro des compétences
    #par contre pour le moement la méthodes n'est pas connecté à la bd donc pas de requete sql pour insertion il faut ajouter
    #ça sert à rien ???? on peut le retirer c'est uniquement la stats des etudats, fomartion trouvé comparér aux insert
    
   

    
    #on peut utiliser cette méthode pour les statiques d'une cohorte. 
    #si on veut qu'une branche de la cohorte affiche des stats, on doit utiliser cette méthodes x fois
    #donc une branche du diagramme SANKEY sera une liste de INE et à partir de cette liste on va faire des stat avec leur notes, décisions etc.

    #MAIS la bdd peut se charger de cette recherche pas besoin de demander à chaque fois à l'API donc transformation 
    # par une requetes SQL qui renverra un objet etudiant ou un dictionnaire

    def get_donnees_etudiant_completes(self, ine: str) -> Optional[Dict]:
        """
        Récupère toutes les données d'un étudiant via son INE
        
        Args:
            ine: Numéro INE de l'étudiant
            
        Returns:
            Dict: Toutes les données de l'étudiant ou None si non trouvé
        """
        # Recherche de l'étudiant par INE
        endpoint = f"/api/v1/etudiants/recherche"
        params = {'ine': ine}
        
        result = self._make_request(endpoint, params=params)
        if not result or not result.get('etudiants'):
            return None
            
        etudiant = result['etudiants'][0]
        etudiant_id = etudiant['id']
        
        # Récupérer les inscriptions
        inscriptions = self.get_inscriptions_etudiant(etudiant_id)
        
        # Pour chaque inscription, récupérer les détails
        for inscription in inscriptions:
            formation_id = inscription.get('formation_id')
            if formation_id:
                # Décisions
                inscription['decisions'] = self.get_decisions_etudiant(
                    etudiant_id, 
                    formation_id
                )
                # Compétences
                inscription['competences'] = self.get_competences_etudiant(
                    etudiant_id, 
                    formation_id
                )
        
        etudiant['inscriptions'] = inscriptions
        
        return etudiant
    