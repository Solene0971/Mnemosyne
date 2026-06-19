# SAE401
Sujet de M. Hébert  - Mnémosyne

> **"Garder la mémoire, éclairer les parcours."**

![Logo Mnémosyne](app/static/img/logo_mnemosyne.png)

## 📄 Contexte

Depuis la réforme de septembre 2021, les IUT ont basculé vers le **Bachelor Universitaire de Technologie (BUT)**. Cette transition a introduit de nouveaux parcours, une approche par compétences (SAÉ) et une complexité accrue dans le suivi de la scolarité.

Ce projet a été développé pour l'**IUT de Villetaneuse** qui compte 6 départements (CJ, GEA, GEII, INFO, RT, SD)  sans oublier les passerelles. Il répond à un besoin crucial de l'institution, du rectorat et du ministère : **le suivi des cohortes**.

Une *cohorte* désigne l'ensemble des étudiants commençant une formation donnée la même année et suivant leur parcours ensemble. Mnémosyne permet de visualiser ce flux complexe sur les 3 années du diplôme.

## ✨ Fonctionnalités

La plateforme est divisée en deux espaces distincts :

### 👁️ Espace consultation (Visualisation)
L'interface permet aux utilisateurs de visualiser les parcours étudiants via des **diagrammes de Sankey**.

* **Filtres dynamiques :** Choix par année de promotion et par département (ou vision globale "Tout l'IUT").
* **Visualisation des flux :** Représentation graphique des passages (BUT1 -> BUT2), redoublements, et abandons.
* **Interactivité :**
    * Clic sur un flux pour **rediriger** vers les détails (ex: suivre spécifiquement les redoublants).
    * Affichage des décisions de jury (ADM, PASD, RED, NAR, ADJ).
* **Statistiques :** Affichage d'indicateurs de performance (taux de passage, taux de diplomation, répartition des origines, etc.).
* **Export PDF :** Possibilité de télécharger un rapport au format PDF contenant le diagramme et les statistiques.

### ⚙️ Espace administration
Réservé à la gestion des données et des règles métier.

* **Synchronisation API :** Bouton pour charger/mettre à jour les données depuis l'API ScoDoc.
* **Gestion des règles d'analyse  :** Configuration des conditions personnalisées pour analyser les parcours étudiants (ex: identifier les étudiants en difficulté selon des critères définis par l'utilisateur). Ces règles permettent de qualifier automatiquement les situations (réussite, alerte, etc.).
* **Gestion des administrateurs :** Possibilité d'ajouter et de gérer l'accès à d'autres administrateurs.
* **Initialisation de la base de données :** Réinitialisation complète de la base avec les données par défaut.

## 🛠️ Stack technique

* **Frontend :** HTML5, CSS3, JavaScript (Bibliothèque de visualisation Sankey).
* **Backend :** Flask (envisage de migrer vers du PHP).
* **Base de Données :** SQLite3.
* **Source de données :** API [ScoDoc 9](https://scodoc.org/ScoDoc9API/).

> **Note sur la confidentialité :** L'accès à l'API de production de l'IUT est restreint. L'environnement de développement utilise des jeux de données anonymisé au format JSON pour simuler les réponses de l'API tout en respectant le RGPD.


## 🚀 Installation et démarrage

### 📋 Prérequis

Avant de commencer, assurez-vous d'avoir installé :

| Outil | Version minimale | Téléchargement |
|-------|------------------|----------------|
| **Python** | 3.8+ | [python.org](https://www.python.org/downloads/) |
| **Git** | 2.0+ | [git-scm.com](https://git-scm.com/downloads) |
| **Pip** | (inclus avec Python) | - |

---

### 1️⃣ Cloner le dépôt

```bash
# Cloner le projet depuis GitHub
git clone https://github.com/Solene0971/Mnemosyne.git

# Se déplacer dans le dossier du projet
cd Mnemosyne