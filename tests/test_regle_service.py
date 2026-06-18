import pytest
from app.services.RegleService import RegleService

@pytest.fixture
def service_regles(mocker):
    """Fixture qui prépare un RegleService avec un mock pour RegleDAO."""
    mocker.patch('app.services.RegleService.RegleDAO')
    return RegleService()


def test_ajouter_regle(service_regles):
    # Arrange
    service_regles.rdao.ajouter_regle.return_value = True
    
    # Act
    resultat = service_regles.ajouter_regle("Exclure DEM", "Exclut les démissionnaires", "etat != 'D'")
    
    # Assert
    assert resultat is True
    service_regles.rdao.ajouter_regle.assert_called_once_with("Exclure DEM", "Exclut les démissionnaires", "etat != 'D'")


def test_modifier_statut(service_regles):
    # Arrange
    service_regles.rdao.modifier_statut.return_value = True
    
    # Act
    resultat = service_regles.modifier_statut(1, True)
    
    # Assert
    assert resultat is True
    service_regles.rdao.modifier_statut.assert_called_once_with(1, True)


def test_get_regles(service_regles):
    # Arrange
    donnees_factices = [{"id": 1, "nom": "Règle 1"}]
    service_regles.rdao.get_regles.return_value = donnees_factices
    
    # Act
    resultat = service_regles.get_regles()
    
    # Assert
    assert resultat == donnees_factices
    service_regles.rdao.get_regles.assert_called_once()


def test_supprimer_regle(service_regles):
    # Arrange
    service_regles.rdao.supprimer_regle.return_value = True
    
    # Act
    resultat = service_regles.supprimer_regle(5)
    
    # Assert
    assert resultat is True
    service_regles.rdao.supprimer_regle.assert_called_once_with(5)


def test_finSQL(service_regles):
    # Arrange
    chaine_sql = " AND etat != 'D'"
    service_regles.rdao.finSQL.return_value = chaine_sql
    
    # Act
    resultat = service_regles.finSQL()
    
    # Assert
    assert resultat == chaine_sql
    service_regles.rdao.finSQL.assert_called_once()