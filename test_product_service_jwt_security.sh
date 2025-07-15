#!/bin/bash

# Script de test pour la sécurité DDD avec JWT synchronisé
# Test des décorateurs JWT du product-service

echo "=== Test de sécurité DDD JWT pour Product Service ==="

# Configuration
PRODUCT_SERVICE_URL="http://localhost:5002"
CUSTOMER_SERVICE_URL="http://localhost:5005"
API_TOKEN="Supermarcher22102002"
BASE_URL="http://localhost:5002"

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo "✅ $2"
    else
        echo "❌ $2"
    fi
}

# Test 1: Vérifier l'authentification - endpoints GET (authenticated_required)
echo -e "\n📋 Test 1: Endpoints GET avec @authenticated_required"

# Test sans token
echo "Test GET /products sans token:"
curl -s -o /dev/null -w "%{http_code}" -X GET "$BASE_URL/products"
echo ""

# Test avec token invalide
echo "Test GET /products avec token invalide:"
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer invalid_token" -X GET "$BASE_URL/products"
echo ""

# Test 2: Obtenir un token JWT valide
echo -e "\n🔐 Test 2: Obtention d'un token JWT valide"

# Connexion client
echo "Connexion client:"
CLIENT_RESPONSE=$(curl -s -X POST "$CUSTOMER_SERVICE_URL/api/customers/login" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "jean.dupont@email.com",
        "password": "password123"
    }')

CLIENT_TOKEN=$(echo "$CLIENT_RESPONSE" | jq -r '.access_token // empty')
echo "Token client: ${CLIENT_TOKEN:0:50}..."

# Connexion responsable produit
echo "Connexion responsable produit:"
RESP_RESPONSE=$(curl -s -X POST "$CUSTOMER_SERVICE_URL/api/customers/login" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "marie.martin@email.com",
        "password": "password123"
    }')

RESP_TOKEN=$(echo "$RESP_RESPONSE" | jq -r '.access_token // empty')
echo "Token responsable: ${RESP_TOKEN:0:50}..."

# Connexion admin
echo "Connexion admin:"
ADMIN_RESPONSE=$(curl -s -X POST "$CUSTOMER_SERVICE_URL/api/customers/login" \
    -H "Authorization: Bearer $API_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "email": "admin@supermarcher.com",
        "password": "admin123"
    }')

ADMIN_TOKEN=$(echo "$ADMIN_RESPONSE" | jq -r '.access_token // empty')
echo "Token admin: ${ADMIN_TOKEN:0:50}..."

# Test 3: Endpoints GET avec tokens valides (authenticated_required)
echo -e "\n📖 Test 3: Endpoints GET avec tokens valides"

if [ -n "$CLIENT_TOKEN" ] && [ "$CLIENT_TOKEN" != "null" ]; then
    echo "Test GET /products avec token client:"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $CLIENT_TOKEN" -X GET "$BASE_URL/products"
    echo ""
    
    echo "Test GET /products/1 avec token client:"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $CLIENT_TOKEN" -X GET "$BASE_URL/products/1"
    echo ""
    
    echo "Test GET /products/search avec token client:"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $CLIENT_TOKEN" -X GET "$BASE_URL/products/search?q=test"
    echo ""
else
    echo "❌ Impossible d'obtenir un token client valide"
fi

# Test 4: Endpoints POST/PUT/DELETE avec @responsable_produit_required
echo -e "\n🔨 Test 4: Endpoints CRUD avec @responsable_produit_required"

# Test avec token client (devrait échouer)
if [ -n "$CLIENT_TOKEN" ] && [ "$CLIENT_TOKEN" != "null" ]; then
    echo "Test POST /products avec token client (devrait échouer):"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $CLIENT_TOKEN" \
        -H "Content-Type: application/json" \
        -X POST "$BASE_URL/products" \
        -d '{
            "name": "Test Product",
            "price": 10.99,
            "category": "test"
        }'
    echo ""
fi

# Test avec token responsable produit (devrait réussir)
if [ -n "$RESP_TOKEN" ] && [ "$RESP_TOKEN" != "null" ]; then
    echo "Test POST /products avec token responsable produit (devrait réussir):"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $RESP_TOKEN" \
        -H "Content-Type: application/json" \
        -X POST "$BASE_URL/products" \
        -d '{
            "name": "Test Product Responsable",
            "price": 15.99,
            "category": "test",
            "description": "Test description"
        }'
    echo ""
    
    echo "Test PUT /products/1 avec token responsable produit:"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $RESP_TOKEN" \
        -H "Content-Type: application/json" \
        -X PUT "$BASE_URL/products/1" \
        -d '{
            "name": "Updated Product",
            "price": 20.99
        }'
    echo ""
    
    echo "Test DELETE /products/999 avec token responsable produit:"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $RESP_TOKEN" \
        -X DELETE "$BASE_URL/products/999"
    echo ""
fi

# Test 5: Endpoint PUT /products/<id>/stock avec @management_required
echo -e "\n📦 Test 5: Endpoint stock avec @management_required"

# Test avec token client (devrait échouer)
if [ -n "$CLIENT_TOKEN" ] && [ "$CLIENT_TOKEN" != "null" ]; then
    echo "Test PUT /products/1/stock avec token client (devrait échouer):"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $CLIENT_TOKEN" \
        -H "Content-Type: application/json" \
        -X PUT "$BASE_URL/products/1/stock" \
        -d '{
            "quantity": 100
        }'
    echo ""
fi

# Test avec token responsable produit (devrait échouer)
if [ -n "$RESP_TOKEN" ] && [ "$RESP_TOKEN" != "null" ]; then
    echo "Test PUT /products/1/stock avec token responsable produit (devrait échouer):"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $RESP_TOKEN" \
        -H "Content-Type: application/json" \
        -X PUT "$BASE_URL/products/1/stock" \
        -d '{
            "quantity": 150
        }'
    echo ""
fi

# Test avec token admin (devrait réussir)
if [ -n "$ADMIN_TOKEN" ] && [ "$ADMIN_TOKEN" != "null" ]; then
    echo "Test PUT /products/1/stock avec token admin (devrait réussir):"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $ADMIN_TOKEN" \
        -H "Content-Type: application/json" \
        -X PUT "$BASE_URL/products/1/stock" \
        -d '{
            "quantity": 200
        }'
    echo ""
fi

# Test 6: Vérification de la synchronisation des clés JWT
echo -e "\n🔑 Test 6: Vérification de la synchronisation des clés JWT"

echo "Vérification que les tokens générés par customer-service sont valides pour product-service:"
if [ -n "$CLIENT_TOKEN" ] && [ "$CLIENT_TOKEN" != "null" ]; then
    echo "Test validation croisée token client:"
    curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $CLIENT_TOKEN" -X GET "$BASE_URL/products"
    echo ""
fi

echo -e "\n🎯 Résumé des tests:"
echo "- Les endpoints GET utilisent @authenticated_required (tous les utilisateurs connectés)"
echo "- Les endpoints POST/PUT/DELETE produits utilisent @responsable_produit_required"
echo "- L'endpoint PUT /products/<id>/stock utilise @management_required"
echo "- Les clés JWT sont synchronisées entre customer-service et product-service"

echo -e "\n✅ Tests terminés!"
