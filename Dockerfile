# 1. on part d'une image Python version slim donc allégé
FROM python:3.11-slim

# 2. on définit le dossier de travail à l'intérieur du conteneur
WORKDIR /app

# 3. on copie le fichier des dépendances en premier (pour optimiser le cache Docker)
COPY requirements.txt .

# 4. on installe les dépendances + Gunicorn (le serveur de production)
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

# 5. on copie tout le reste du code du projet dans le conteneur
COPY . .

# 6. on indique que l'application va communiquer sur le port 5000
EXPOSE 5000

# 7. la commande pour démarrer l'application avec Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]