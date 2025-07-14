#!/bin/bash

echo "=========================================="
echo "=== DIAGNOSTIC ET CORRECTION FINALE ==="
echo "=========================================="

echo "🔍 DIAGNOSTIC COMPLET"
echo "===================="

echo "1. Vérification git conflict..."
git status | grep -E "(both modified|merge|conflict)" && echo "❌ CONFLIT GIT DÉTECTÉ" || echo "✅ Git propre"

echo ""
echo "2. État des conteneurs..."
docker-compose -f docker-compose-microservices.yml ps | grep -E "(Restarting|Exit)"

echo ""
echo "3. Logs du customer-service (10 dernières lignes)..."
docker-compose -f docker-compose-microservices.yml logs customer-service --tail=10

echo ""
echo "4. Vérification du réseau Docker..."
docker network ls | grep microservices

echo ""
echo "🛠️ CORRECTIONS ÉTAPE PAR ÉTAPE"
echo "==============================="

echo ""
echo "ÉTAPE 1: Résolution conflit git"
echo "------------------------------"
git stash
git pull origin lab5
# Ne pas restaurer le stash pour éviter les conflits

echo ""
echo "ÉTAPE 2: Arrêt complet"
echo "--------------------"
docker-compose -f docker-compose-microservices.yml down
sleep 5

echo ""
echo "ÉTAPE 3: Nettoyage Docker"
echo "------------------------"
docker system prune -f

echo ""
echo "ÉTAPE 4: Rebuild customer-service spécifiquement"
echo "-----------------------------------------------"
docker-compose -f docker-compose-microservices.yml build --no-cache customer-service

echo ""
echo "ÉTAPE 5: Démarrage en mode debug"
echo "-------------------------------"
docker-compose -f docker-compose-microservices.yml up -d

echo ""
echo "ÉTAPE 6: Attente et monitoring"
echo "-----------------------------"
echo "Attente 30 secondes pour stabilisation..."
sleep 30

echo ""
echo "État des services:"
docker-compose -f docker-compose-microservices.yml ps

echo ""
echo "ÉTAPE 7: Test de connectivité interne"
echo "------------------------------------"
echo "Test ping customer-service depuis api-gateway:"
docker-compose -f docker-compose-microservices.yml exec -T api-gateway ping -c 2 customer-service 2>/dev/null && echo "✅ DNS OK" || echo "❌ DNS FAILED"

echo ""
echo "ÉTAPE 8: Test API direct"
echo "----------------------"
echo "Test health customer-service:"
curl -s http://localhost:5005/health && echo "✅ Customer service OK" || echo "❌ Customer service FAILED"

echo ""
echo "Test login direct:"
curl -s -X POST -H "Content-Type: application/json" -H "Authorization: Bearer Supermarcher22102002" \
  -d '{"email": "gestionnaire@maisonmere.com", "password": "gestionnaire123"}' \
  http://localhost:5005/api/customers/login | grep -o "Connexion réussie\|successful" && echo "✅ Login OK" || echo "❌ Login FAILED"

echo ""
echo "ÉTAPE 9: Test via API Gateway"
echo "----------------------------"
echo "Test de connexion via web interface:"
curl -s -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=gestionnaire&password=gestionnaire123" \
  http://localhost:5000/login | grep -o "Connexion réussie\|admin\|Marie" && echo "✅ Web login OK" || echo "❌ Web login FAILED"

echo ""
echo "🎯 RÉSUMÉ FINAL"
echo "==============="
echo ""
if docker-compose -f docker-compose-microservices.yml ps | grep -q "customer-service.*Up"; then
    echo "✅ Customer service: UP"
else
    echo "❌ Customer service: DOWN - Vérifiez les logs"
fi

if curl -s http://localhost:5000/health | grep -q "healthy"; then
    echo "✅ API Gateway: HEALTHY"
else
    echo "❌ API Gateway: UNHEALTHY"
fi

echo ""
echo "🚀 COMMANDES FINALES"
echo "==================="
echo ""
echo "Si tout semble OK, lancez:"
echo "   ./test_vm_complete.sh"
echo ""
echo "Si customer-service redémarre encore:"
echo "   docker-compose -f docker-compose-microservices.yml logs customer-service"
echo ""
echo "Pour test manuel du login:"
echo "   curl -X POST -H 'Content-Type: application/x-www-form-urlencoded' \\"
echo "        -d 'username=gestionnaire&password=gestionnaire123' \\"
echo "        http://localhost:5000/login"
echo ""
