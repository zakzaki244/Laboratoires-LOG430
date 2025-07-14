FROM python:3.9-slim

WORKDIR /app

# Installer netcat pour wait-for-db.sh
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Rendre le script d'attente exécutable
RUN chmod +x wait-for-db.sh

EXPOSE 5002

CMD ["./wait-for-db.sh", "db-products", "5432", "python", "app_ddd.py"]
