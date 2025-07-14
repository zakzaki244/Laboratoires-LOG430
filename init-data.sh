#!/bin/bash

# Script d'initialisation des données pour tous les microservices
# À exécuter après le démarrage de tous les services

echo "=== Initialisation des données pour les microservices ==="

# Attendre que les services soient prêts
echo "Attente du démarrage des services..."
sleep 10

# Variables d'environnement
API_BASE_URL="http://localhost"
GATEWAY_PORT="5000"
CUSTOMER_PORT="5005"
PRODUCT_PORT="5001"
STORE_PORT="5002"
INVENTORY_PORT="5003"
SALES_PORT="5004"

echo "=== Test de santé des services ==="
curl -s "$API_BASE_URL:$CUSTOMER_PORT/health" || echo "Customer service non disponible"
curl -s "$API_BASE_URL:$GATEWAY_PORT/health" || echo "API Gateway non disponible"

echo -e "\n=== Identifiants de test disponibles ==="
echo "Les utilisateurs suivants sont automatiquement créés au démarrage:"
echo "1. admin@test.com / admin123 (Administrateur)"
echo "2. user@test.com / user123 (Utilisateur)"
echo "3. manager@test.com / manager123 (Gestionnaire)"
echo "4. client@test.com / client123 (Client)"
echo "5. demo@test.com / demo123 (Compte de démonstration)"

echo -e "\n=== Création de données de test supplémentaires ==="

# Exemple de données produits (si le service est disponible)
echo "Création de produits de test..."
# curl -X POST "$API_BASE_URL:$PRODUCT_PORT/api/products" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "name": "Produit Test 1",
#     "description": "Description du produit test",
#     "price": 29.99,
#     "category": "Test"
#   }' || echo "Service produits non disponible"

# Exemple de données magasins (si le service est disponible)
echo "Création de magasins de test..."
# curl -X POST "$API_BASE_URL:$STORE_PORT/api/stores" \
#   -H "Content-Type: application/json" \
#   -d '{
#     "name": "Magasin Test Montreal",
#     "address": "123 Test Street, Montreal, QC",
#     "phone": "514-123-4567"
#   }' || echo "Service magasins non disponible"

echo -e "\n=== Initialisation terminée ==="
echo "Vous pouvez maintenant vous connecter avec les identifiants ci-dessus"
echo "URL de connexion: http://10.194.32.174/login"
