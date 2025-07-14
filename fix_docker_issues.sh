#!/bin/bash

echo "=== NETTOYAGE COMPLET ET RECONSTRUCTION ==="
echo "$(date)"

# 1. Arrêter tous les conteneurs
echo "1. Arrêt de tous les conteneurs..."
docker-compose -f docker-compose-microservices.yml down

# 2. Supprimer les conteneurs problématiques
echo "2. Suppression des conteneurs problématiques..."
docker rm -f $(docker ps -aq --filter "name=customer-service") 2>/dev/null || true
docker rm -f $(docker ps -aq --filter "name=inventory-service") 2>/dev/null || true

# 3. Supprimer les images problématiques
echo "3. Suppression des images problématiques..."
docker rmi -f laboratoire-log430_customer-service 2>/dev/null || true
docker rmi -f laboratoire-log430_inventory-service 2>/dev/null || true

# 4. Nettoyer le cache Docker
echo "4. Nettoyage du cache Docker..."
docker system prune -f

# 5. Reconstruire COMPLÈTEMENT les services problématiques
echo "5. Reconstruction complète des services..."
docker-compose -f docker-compose-microservices.yml build --no-cache --force-rm customer-service inventory-service

# 6. Redémarrer tous les services
echo "6. Redémarrage de tous les services..."
docker-compose -f docker-compose-microservices.yml up -d

# 7. Attendre le démarrage
echo "7. Attente du démarrage (60 secondes)..."
sleep 60

# 8. Vérifier l'état
echo "8. Vérification de l'état..."
docker-compose -f docker-compose-microservices.yml ps

# 9. Vérifier les logs
echo "=== LOGS CUSTOMER SERVICE ==="
docker-compose -f docker-compose-microservices.yml logs customer-service | tail -15

echo "=== LOGS INVENTORY SERVICE ==="
docker-compose -f docker-compose-microservices.yml logs inventory-service | tail -15

# 10. Test final
echo "=== TEST FINAL ==="
./test_vm_complete.sh

echo "=== TERMINÉ ==="
