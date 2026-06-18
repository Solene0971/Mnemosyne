import pytest
from app.services.DonneeService import DonneeService

@pytest.fixture
def service_sankey(mocker):
    """
    Fixture pytest : Prépare une instance de DonneeService 
    avec un DonneeDAO factice (mocké) pour ne pas utiliser la vraie BDD.
    """
    mocker.patch('app.services.DonneeService.DonneeDAO')
    service = DonneeService()
    return service

def test_get_sankey_stats_cas_nominal(service_sankey):
    """
    Test le comportement normal : des paramètres valides sont passés, 
    le DAO est appelé et renvoie des données.
    """
    # Arrange
    donnees_attendues = {'but1': 200, 'but2': 180, 'but3_diplome': 150}
    # On configure le mock pour qu'il renvoie nos données factices
    service_sankey.dao.get_sankey_data.return_value = donnees_attendues

    # Act
    resultat = service_sankey.get_sankey_stats(year=2023, dept='INFO', rythme='FI', regles_sql="")

    # Assert
    assert resultat == donnees_attendues
    # Ajout de [] car regles_params par défaut est une liste vide
    service_sankey.dao.get_sankey_data.assert_called_once_with(2023, 'INFO', 'FI', "", [])

def test_get_sankey_stats_sans_annee(service_sankey):
    """
    Test la règle de gestion : si l'année (year) est absente, 
    la fonction doit retourner None sans appeler la BDD.
    """
    # Act
    resultat = service_sankey.get_sankey_stats(year=None, dept='INFO', rythme='FI', regles_sql="")

    # Assert
    assert resultat is None
    # On vérifie que la base de données n'a pas été sollicitée du tout
    service_sankey.dao.get_sankey_data.assert_not_called()

def test_get_sankey_stats_exception_bdd(service_sankey, capsys):
    """
    Test la résilience : si la base de données plante, 
    l'exception doit être capturée, un print doit être fait, et la fonction retourne None.
    """
    # Arrange : on force le mock du DAO à lever une exception
    service_sankey.dao.get_sankey_data.side_effect = Exception("Erreur fatale BDD")

    # Act
    resultat = service_sankey.get_sankey_stats(year=2023, dept='INFO', rythme='FI', regles_sql="")

    # Assert
    assert resultat is None
    service_sankey.dao.get_sankey_data.assert_called_once()
    
    # On vérifie que le message d'erreur a bien été affiché dans la console (comportement de votre try/except)
    captured = capsys.readouterr()
    assert "Erreur calcul Sankey : Erreur fatale BDD" in captured.out