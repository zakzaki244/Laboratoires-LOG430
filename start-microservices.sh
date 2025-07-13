#!/bin/bash

# Script de démarrage pour l'architecture microservices
echo "🚀 Démarrage de l'architecture microservices e-commerce..."

# Nettoyer les anciens conteneurs
echo "🧹 Nettoyage des anciens conteneurs..."
docker-compose -f docker-compose-microservices.yml down

# Construire les images
echo "🏗️ Construction des images Docker..."
docker-compose -f docker-compose-microservices.yml build

# Démarrer les services
echo "🚀 Démarrage des services..."
docker-compose -f docker-compose-microservices.yml up -d

# Attendre que les services soient prêts
echo "⏳ Attente du démarrage des services..."
sleep 30

# Vérifier l'état des services
echo "🔍 Vérification de l'état des services..."
curl -s http://localhost:5000/health || echo "❌ API Gateway non disponible"
curl -s http://localhost:5001/health || echo "❌ Store Service non disponible"
curl -s http://localhost:5002/health || echo "❌ Product Service non disponible"
curl -s http://localhost:5003/health || echo "❌ Sales Service non disponible"
curl -s http://localhost:5004/health || echo "❌ Inventory Service non disponible"
curl -s http://localhost:5005/health || echo "❌ Customer Service non disponible"
curl -s http://localhost:5006/health || echo "❌ Cart Service non disponible"
curl -s http://localhost:5007/health || echo "❌ Checkout Service non disponible"

echo "✅ Architecture microservices démarrée!"
echo "🌐 API Gateway: http://localhost:5000"
echo "🏪 Store Service: http://localhost:5001"
echo "🛍️ Product Service: http://localhost:5002"
echo "💰 Sales Service: http://localhost:5003"
echo "📦 Inventory Service: http://localhost:5004"
echo "👥 Customer Service: http://localhost:5005"
echo "🛒 Cart Service: http://localhost:5006"
echo "✅ Checkout Service: http://localhost:5007"
echo "📊 Prometheus: http://localhost:9090"
echo "📈 Grafana: http://localhost:3000"
echo "🔄 Load Balancer: http://localhost:80"
