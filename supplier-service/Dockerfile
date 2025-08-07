FROM python:3.11-slim

WORKDIR /app

# Copier et installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY . .

# Variables d'environnement
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV MIN_DELIVERY_DAYS=1
ENV MAX_DELIVERY_DAYS=7

# Exposer le port
EXPOSE 5000

# Commande de démarrage
CMD ["python", "app.py"]
