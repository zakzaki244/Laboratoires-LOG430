#!/bin/bash
# wait-for-db.sh - Script pour attendre que la base de données soit prête

set -e

host="$1"
port="$2"
shift 2
cmd="$@"

until nc -z "$host" "$port"; do
  echo "Waiting for database at $host:$port..."
  sleep 2
done

echo "Database is ready! Starting service..."
exec $cmd
