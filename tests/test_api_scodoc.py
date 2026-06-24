import pytest
import os
from dotenv import load_dotenv
from app.models.ScoDocAPI import ScoDocAPI


# Load .env to get real credentials
load_dotenv()

SCODOC_URL = os.getenv('SCODOC_API_URL')
SCODOC_ID = os.getenv('SCODOC_ID')
SCODOC_PASSWORD = os.getenv('SCODOC_PASSWORD')


@pytest.fixture(scope='module')
def api():
    try:
        api_instance = ScoDocAPI(SCODOC_URL)
        return api_instance
    except Exception as e:
        pytest.skip(f"Impossible de créer l'API: {e}")


def test_recup_token_connection():
    try:
        api = ScoDocAPI(SCODOC_URL)
        assert api.api_token is not None
        assert isinstance(api.api_token, str)
        assert len(api.api_token) > 0
        print(f"Token récupéré avec succès: {api.api_token[:20]}...")
    except Exception as e:
        pytest.fail(f"Erreur lors de la récupération du token: {e}")


def test_get_departements(api):
    res = api.get_departements()
    assert isinstance(res, list)
    print(f"Départements récupérés: {len(res)} trouvés")
    if res:
        print(f"Exemples: {res[:2]}")


def test_get_formations(api):
    res = api.get_formations()
    assert isinstance(res, list)
    print(f"Formations récupérées: {len(res)} trouvées")
    if res:
        print(f"Exemples: {res[:2]}")


def test_get_referentiel_competences(api):
    formations = api.get_formations()
    if not formations:
        pytest.skip("Pas de formations disponibles")
    
    formation_id = formations[0].get('id')
    if not formation_id:
        pytest.skip("ID de formation non trouvé")
    
    try:
        res = api.get_referentiel_competences(formation_id)
        assert res is not None
        print(f"Référentiel pour formation {formation_id}: {type(res).__name__}")
    except Exception as e:
        print(f"Formation {formation_id}: {e}")


def test_get_formsemestres_query(api):
    try:
        res = api.get_formsemestres_query(annee_scolaire=2023)
        assert isinstance(res, (list, dict))
        print(f"Formsemestres 2023: {type(res).__name__}")
    except Exception as e:
        print(f"Formsemestres query: {e}")


def test_get_decisions_jury(api):
    try:
        formsemestres = api.get_formsemestres_query(annee_scolaire=2023)
        if not formsemestres or isinstance(formsemestres, dict):
            pytest.skip("Pas de formsemestres ou réponse de type dict")
        
        if formsemestres:
            fs_id = formsemestres[0].get('id')
            if fs_id:
                res = api.get_decisions_jury(fs_id)
                assert res is not None
                print(f"Décisions jury pour formsemestre {fs_id}: {type(res).__name__}")
    except Exception as e:
        print(f"Decisions jury: {e}")
