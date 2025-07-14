#!/bin/bash
# Script d'attente pour la base de données
set -e

host="$1"
port="$2"
shift 2
cmd="$@"

echo "Attente de la base de données $host:$port..."

# Attendre que la base de données soit prête
while ! nc -z "$host" "$port"; do
  echo "Base de données non prête, attente 5 secondes..."
  sleep 5
done

echo "Base de données prête, démarrage du service..."
exec $cmd
