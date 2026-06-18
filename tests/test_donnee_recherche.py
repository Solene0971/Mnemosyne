import pytest
from app.services.DonneeService import DonneeService

@pytest.fixture
def service_donnees(mocker):
    mocker.patch('app.services.DonneeService.DonneeDAO')
    return DonneeService()


def test_get_search_results_sans_annee(service_donnees):
    """Test que la fonction retourne une liste vide si l'année n'est pas fournie."""
    resultats = service_donnees.get_search_results(year=None, dept='INFO', rythme='FI', regles="")
    
    assert resultats == []
    service_donnees.dao.search_etudiants.assert_not_called()


def test_get_search_results_annee_invalide(service_donnees):
    """Test que la fonction gère la ValueError (lettres au lieu de chiffres pour l'année)."""
    # L'année "vingt" va faire planter int("vingt"), ce qui déclenche le except ValueError
    resultats = service_donnees.get_search_results(year="vingt", dept='INFO', rythme='FI', regles="")
    
    assert resultats == []
    service_donnees.dao.search_etudiants.assert_not_called()


def test_get_search_results_succes(service_donnees):
    """Test le fonctionnement normal de la recherche et la création des objets EtudiantView."""
    # Arrange : Simulation des données renvoyées par la BDD
    lignes_bdd = [
        {
            'ine': '123456789', 
            'annee_universitaire': 2023, 
            'annee_but': 1, 
            'resultat': 'ADM', 
            'dept': 'INFO', 
            'rythme': 'FI'
        }
    ]
    service_donnees.dao.search_etudiants.return_value = lignes_bdd

    # Act
    resultats = service_donnees.get_search_results(year="2023", dept='INFO', rythme='FI', regles="")

    # Assert
    assert len(resultats) == 1
    # On vérifie que la ligne SQL a bien été transformée en objet (on peut appeler .ine)
    assert resultats[0].ine == '123456789'
    assert resultats[0].resultat == 'ADM'
    
    # On vérifie que la string "2023" a bien été convertie en int(2023) avant d'appeler le DAO
    service_donnees.dao.search_etudiants.assert_called_once_with(2023, 'INFO', 'FI', "")