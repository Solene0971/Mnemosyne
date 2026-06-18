import pytest
from app.services.DonneeService import DonneeService

@pytest.fixture
def service_sankey(mocker):
    """
    Fixture pytest : Prépare une instance de DonneeService avec un DonneeDAO (mocké) pour ne pas utiliser la vraie BDD.
    """
    mocker.patch('app.services.DonneeService.DonneeDAO') # on mock la classe DonneeDAO au moment où elle est importée dans DonneeService
    service = DonneeService()
    return service


def test_get_sankey_stats_cas_nominal(service_sankey):
    """
    Test le comportement normal : des paramètres valides sont passés, le DAO est appelé et renvoie des données.
    """
    # Arrange
    donnees_attendues = {'but1': 200, 'but2': 180, 'but3_diplome': 150}
    service_sankey.dao.get_sankey_data.return_value = donnees_attendues # on conifg le mock pour qu'il nous renvoie nos données factices

    # Act
    resultat = service_sankey.get_sankey_stats(year=2023, dept='INFO', rythme='FI', regles=[])

    # Assert
    assert resultat == donnees_attendues
    service_sankey.dao.get_sankey_data.assert_called_once_with(2023, 'INFO', 'FI', []) # on vérifie que le DAO a bien été appelé avec les bons paramètres


def test_get_sankey_stats_sans_annee(service_sankey):
    """
    Test la règle de gestion : si l'année est absente, la fonction doit retourner None sans appeler la BDD.
    """
    # Act
    resultat = service_sankey.get_sankey_stats(year=None, dept='INFO', rythme='FI', regles=[])

    # Assert
    assert resultat is None
    service_sankey.dao.get_sankey_data.assert_not_called() # on vérifie que la base de données n'a pas été sollicitée du tout


def test_get_sankey_stats_exception_bdd(service_sankey, capsys):
    """
    Test la résilience : si la base de données plante, l'exception doit être capturée, un print doit être fait, et la fonction retourne None.
    """
    # Arrange : on force le mock du DAO à lever une exception
    service_sankey.dao.get_sankey_data.side_effect = Exception("Erreur fatale BDD")

    # Act
    resultat = service_sankey.get_sankey_stats(year=2023, dept='INFO', rythme='FI', regles=[])

    # Assert
    assert resultat is None
    service_sankey.dao.get_sankey_data.assert_called_once()
    
    # on vérifie que le message d'erreur a bien été affiché dans la console
    captured = capsys.readouterr() # 
    assert "Erreur calcul Sankey : Erreur fatale BDD" in captured.out