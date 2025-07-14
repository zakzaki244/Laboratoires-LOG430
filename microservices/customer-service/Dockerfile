FROM python:3.9-slim

WORKDIR /app

# Installer netcat pour le script wait-for-db
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Donner les permissions d'exécution au script wait-for-db
RUN chmod +x wait-for-db.sh

EXPOSE 5005

CMD ["./wait-for-db.sh", "db-customers", "5432", "python", "app_ddd.py"]
