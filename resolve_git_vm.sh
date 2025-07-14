#!/bin/bash

# Script de résolution immédiate des conflits git sur VM

echo "=== RÉSOLUTION CONFLITS GIT VM ==="

echo "1. Sauvegarde du fichier en conflit..."
git stash

echo "2. Pull forcé..."
git pull origin lab5

echo "3. Vérification des nouveaux fichiers..."
ls -la final_fix_vm.sh fix_vm_urgent.sh 2>/dev/null || echo "Scripts non trouvés"

echo "4. Permissions..."
chmod +x *.sh 2>/dev/null

echo "5. Test customer-service..."
docker-compose -f docker-compose-microservices.yml ps | grep customer-service

echo "6. Logs customer-service..."
docker-compose -f docker-compose-microservices.yml logs customer-service --tail=10

echo "7. Test direct customer-service health..."
curl -s http://localhost:5005/health || echo "Customer service inaccessible"

echo "8. Test login direct..."
curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer Supermarcher22102002" \
  -d '{"email": "gestionnaire@maisonmere.com", "password": "gestionnaire123"}' \
  http://localhost:5005/api/customers/login | head -n 3

echo "=== FIN RÉSOLUTION ==="
