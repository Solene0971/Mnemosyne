import requests
from typing import Dict, List, Optional, Tuple
from flask import current_app
import os

class ScoDocAPI:
    """Classe pour interagir avec l'API ScoDoc"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        #récupération du token
        self.api_token = self._recupToken()  
        self.headers = {
            'Authorization': f'Bearer {self.api_token}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _getConfig(self)-> Tuple[str, str]:
        """
        Retourne les identifiants pour se connecter à ScoDoc
        """
        id = os.getenv("SCODOC_ID")
        mdp = os.getenv("SCODOC_PASSWORD")
        return id, mdp

    def _recupToken(self) -> str:
        """
        Fonction permettant de récupérer un token pour effectuer des requêtes vers l'API
        Retourne le token OU Lève une exception si la connection vers l'API échoue
        """
        identifiant, mdp = self._getConfig()
        #url vers la récupération du token ScoDoc
        auth_url = f"{self.base_url}/tokens"

        try:
            response = requests.post(auth_url, auth=(identifiant, mdp), timeout=10)
            response.raise_for_status()
            data = response.json()

        except requests.HTTPError as e:
            raise Exception(
                f"Erreur HTTP lors de la récupération du token ScoDoc: {response.status_code}") from e
        except requests.RequestException as e:
            raise Exception(
                f"Impossible de s'authentifier auprès de ScoDoc:\n{e}") from e
        except ValueError as e:
            raise Exception(
                f"Réponse invalide de ScoDoc. Vérifiez que l'API renvoie du JSON valide.") from e

        token = data.get('token')
        if not token:
            raise Exception(
                f"Impossible de récupérer le token depuis ScoDoc. Vérifiez vos identifiants.")

        return token

    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Effectue une requête GET générique"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=60)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(
                f"Impossible de contacter ScoDoc pour {endpoint}. "
                "Vérifiez la connexion réseau et le statut de l'API."
            ) from e
        except ValueError as e:
            raise Exception(
                f"Réponse invalide de ScoDoc pour {endpoint}. "
                "Vérifiez que l'API renvoie du JSON valide."
            ) from e

    # --- DONNÉES STRUCTURELLES ---

    def get_departements(self) -> List[Dict]:
        res = self._make_request("/departements")
        if isinstance(res, list):
            print("departement récupéré sous forme de liste")
            return res
        if isinstance(res, dict):
            print("departement récupéré sous forme de dictionnaire")
            return res.get('departements', [])
        return []

    def get_formations(self) -> List[Dict]:
        """Récupère toutes les formations"""
        res = self._make_request("/formations")
        if isinstance(res, list):
            print("formation récupéré sous forme de liste")
            return res
        if isinstance(res, dict):
            print("formation récupéré sous forme de dictionnaire")
            return res.get('formations', [])
        return []

    def get_referentiel_competences(self, formation_id: int) -> Optional[Dict]:
        """
        Récupère le référentiel (Parcours, Compétences, UE) d'une formation.
        Vital pour remplir les tables 'parcours' et 'competence'.
        """
        return self._make_request(f"/formation/{formation_id}/referentiel_competences")

    # --- DONNÉES ÉTUDIANTS / RÉSULTATS ---

    def get_formsemestres_query(self, annee_scolaire: int) -> List[Dict]:
        """
        Récupère tous les semestres (FormSemestres) d'une année donnée.
        """
        return self._make_request("/formsemestres/query", params={'annee_scolaire': annee_scolaire})

    def get_decisions_jury(self, formsemestre_id: int) -> List[Dict]:
        """
        Récupère TOUS les résultats (étudiants, décisions, moyennes) pour un semestre.
        C'est ici qu'on trouve les notes et les validations de compétences.
        """
        return self._make_request(f"/formsemestre/{formsemestre_id}/decisions_jury")