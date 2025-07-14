#!/bin/bash

echo "=========================================="
echo "=== CORRECTION URGENTE SYSTÈME VM ==="
echo "=========================================="

echo "1. RÉSOLUTION DU CONFLIT GIT"
echo "============================"
echo "Sauvegarde des modifications locales..."
git stash
echo "Pull des modifications..."
git pull origin lab5
echo "Restauration des modifications locales si nécessaire..."
git stash pop 2>/dev/null || echo "Aucune modification locale à restaurer"

echo ""
echo "2. ARRÊT COMPLET ET NETTOYAGE"
echo "============================"
docker-compose -f docker-compose-microservices.yml down
docker system prune -f
docker volume prune -f

echo ""
echo "3. VÉRIFICATION DE LA CONFIGURATION DOCKER-COMPOSE"
echo "================================================"
# Vérifier que les services utilisent les bons noms
grep -n "customer-service" docker-compose-microservices.yml | head -5

echo ""
echo "4. RECONSTRUCTION COMPLÈTE"
echo "=========================="
docker-compose -f docker-compose-microservices.yml build --no-cache

echo ""
echo "5. RELANCEMENT AVEC ATTENTE"
echo "=========================="
docker-compose -f docker-compose-microservices.yml up -d

echo ""
echo "6. ATTENTE DE STABILISATION (90 secondes)"
echo "========================================"
echo "Attente de démarrage des services..."
sleep 30
echo "Encore 60 secondes..."
sleep 30
echo "Encore 30 secondes..."
sleep 30
echo "Services devraient être prêts !"

echo ""
echo "7. VÉRIFICATION DE L'ÉTAT"
echo "======================="
docker-compose -f docker-compose-microservices.yml ps

echo ""
echo "8. VÉRIFICATION DU RÉSEAU DOCKER"
echo "==============================="
echo "Réseaux Docker disponibles:"
docker network ls | grep laboratoire

echo ""
echo "Services dans le réseau:"
docker network inspect laboratoire-log430_microservices-network --format='{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null || echo "Réseau non trouvé"

echo ""
echo "9. TEST DE CONNECTIVITÉ INTERNE"
echo "=============================="
echo "Test de résolution DNS depuis api-gateway vers customer-service:"
docker-compose -f docker-compose-microservices.yml exec -T api-gateway ping -c 2 customer-service 2>/dev/null || echo "❌ Résolution DNS échoue"

echo ""
echo "10. TEST DES SERVICES"
echo "==================="
echo "Customer service health:"
curl -s http://localhost:5005/health || echo "❌ Customer service inaccessible"

echo ""
echo "API Gateway health:"
curl -s http://localhost:5000/health || echo "❌ API Gateway inaccessible"

echo ""
echo "=========================================="
echo "=== CORRECTION TERMINÉE ==="
echo "=========================================="
echo ""
echo "Si les problèmes persistent, vérifiez :"
echo "1. Tous les conteneurs sont 'Up'"
echo "2. Le réseau Docker est créé"
echo "3. La résolution DNS fonctionne"
echo ""
echo "Lancez ensuite : ./test_vm_complete.sh"
echo ""
