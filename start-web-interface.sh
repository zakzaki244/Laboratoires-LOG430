#!/bin/bash

# Script pour démarrer l'interface web de l'API Gateway

echo "🚀 Démarrage de l'interface web E-Commerce..."
echo "================================================"

# Vérifier si Docker est en cours d'exécution
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker n'est pas en cours d'exécution. Veuillez démarrer Docker."
    exit 1
fi

# Vérifier si docker-compose est disponible
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose n'est pas installé."
    exit 1
fi

# Arrêter les conteneurs existants
echo "🛑 Arrêt des conteneurs existants..."
docker-compose -f docker-compose-microservices.yml down

# Construire et démarrer les services
echo "🔧 Construction et démarrage des services..."
docker-compose -f docker-compose-microservices.yml up -d --build

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 15

# Vérifier l'état des services
echo "🔍 Vérification de l'état des services..."
echo ""

services=(
    "api-gateway:5000"
    "store-service:5001"
    "product-service:5002"
    "sales-service:5003"
    "inventory-service:5004"
    "customer-service:5005"
    "cart-service:5006"
    "checkout-service:5007"
)

for service in "${services[@]}"; do
    name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ $name (port $port) - OK"
    else
        echo "❌ $name (port $port) - ERREUR"
    fi
done

echo ""
echo "🎯 Interface web disponible sur:"
echo "   - Accueil: http://localhost:5000"
echo "   - Connexion: http://localhost:5000/login"
echo "   - Status: http://localhost:5000/health-status"
echo ""
echo "🔑 Comptes de test:"
echo "   - Admin: admin / admin"
echo "   - Employé: employe / employe"
echo "   - Client: client / client"
echo ""
echo "📊 Monitoring:"
echo "   - Nginx: http://localhost:8080"
echo "   - Prometheus: http://localhost:9090"
echo "   - Grafana: http://localhost:3000"
echo ""
echo "🔧 Commandes utiles:"
echo "   - Voir les logs: docker-compose -f docker-compose-microservices.yml logs -f"
echo "   - Arrêter: docker-compose -f docker-compose-microservices.yml down"
echo "   - Redémarrer: docker-compose -f docker-compose-microservices.yml restart"
echo ""
echo "✨ Interface web prête ! Ouvrez votre navigateur sur http://localhost:5000"
