#!/bin/bash

# Script de test pour vérifier la sécurité DDD du product-service

BASE_URL="http://localhost:5002"
API_TOKEN="Supermarcher22102002"

echo "🧪 Test de sécurité DDD Product Service"
echo "=========================================="

# Test 1: Obtenir un token JWT pour un client
echo "📝 Test 1: Connexion client pour obtenir un token JWT"
CLIENT_TOKEN=$(curl -s -X POST http://localhost:5005/api/customers/login \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{"email": "client@example.com", "password": "password123"}' | \
  jq -r '.access_token // empty')

if [ -z "$CLIENT_TOKEN" ]; then
  echo "❌ Impossible d'obtenir le token client"
  exit 1
fi

echo "✅ Token client obtenu: ${CLIENT_TOKEN:0:50}..."

# Test 2: Obtenir un token JWT pour un responsable produit
echo "📝 Test 2: Connexion responsable produit pour obtenir un token JWT"
RESPONSABLE_TOKEN=$(curl -s -X POST http://localhost:5005/api/customers/login \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{"email": "responsable.produit@example.com", "password": "password123"}' | \
  jq -r '.access_token // empty')

if [ -z "$RESPONSABLE_TOKEN" ]; then
  echo "❌ Impossible d'obtenir le token responsable produit"
  exit 1
fi

echo "✅ Token responsable produit obtenu: ${RESPONSABLE_TOKEN:0:50}..."

# Test 3: Obtenir un token JWT pour un gestionnaire
echo "📝 Test 3: Connexion gestionnaire pour obtenir un token JWT"
GESTIONNAIRE_TOKEN=$(curl -s -X POST http://localhost:5005/api/customers/login \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_TOKEN" \
  -d '{"email": "gestionnaire@example.com", "password": "password123"}' | \
  jq -r '.access_token // empty')

if [ -z "$GESTIONNAIRE_TOKEN" ]; then
  echo "❌ Impossible d'obtenir le token gestionnaire"
  exit 1
fi

echo "✅ Token gestionnaire obtenu: ${GESTIONNAIRE_TOKEN:0:50}..."

echo ""
echo "🔒 Tests d'accès avec authentification DDD"
echo "============================================"

# Test 4: GET /products - Doit fonctionner pour tous les utilisateurs authentifiés
echo "📝 Test 4: GET /products avec token client (doit réussir)"
RESPONSE=$(curl -s -X GET "$BASE_URL/products" \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -w "%{http_code}")

HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Client peut lister les produits (200)"
else
  echo "❌ Client ne peut pas lister les produits ($HTTP_CODE)"
fi

# Test 5: POST /products - Doit fonctionner seulement pour responsable produit
echo "📝 Test 5: POST /products avec token client (doit échouer)"
RESPONSE=$(curl -s -X POST "$BASE_URL/products" \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "description": "Test", "price": 10.99, "category": "test"}' \
  -w "%{http_code}")

HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "403" ]; then
  echo "✅ Client ne peut pas créer de produits (403 - Accès refusé)"
else
  echo "❌ Client ne devrait pas pouvoir créer de produits ($HTTP_CODE)"
fi

echo "📝 Test 6: POST /products avec token responsable produit (doit réussir)"
RESPONSE=$(curl -s -X POST "$BASE_URL/products" \
  -H "Authorization: Bearer $RESPONSABLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Product", "description": "Test", "price": 10.99, "category": "test"}' \
  -w "%{http_code}")

HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "201" ]; then
  echo "✅ Responsable produit peut créer des produits (201)"
else
  echo "❌ Responsable produit ne peut pas créer de produits ($HTTP_CODE)"
fi

# Test 7: PUT /products/1/stock - Doit fonctionner seulement pour gestionnaire/admin
echo "📝 Test 7: PUT /products/1/stock avec token client (doit échouer)"
RESPONSE=$(curl -s -X PUT "$BASE_URL/products/1/stock" \
  -H "Authorization: Bearer $CLIENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100}' \
  -w "%{http_code}")

HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "403" ]; then
  echo "✅ Client ne peut pas mettre à jour le stock (403 - Accès refusé)"
else
  echo "❌ Client ne devrait pas pouvoir mettre à jour le stock ($HTTP_CODE)"
fi

echo "📝 Test 8: PUT /products/1/stock avec token responsable produit (doit échouer)"
RESPONSE=$(curl -s -X PUT "$BASE_URL/products/1/stock" \
  -H "Authorization: Bearer $RESPONSABLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100}' \
  -w "%{http_code}")

HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "403" ]; then
  echo "✅ Responsable produit ne peut pas mettre à jour le stock (403 - Accès refusé)"
else
  echo "❌ Responsable produit ne devrait pas pouvoir mettre à jour le stock ($HTTP_CODE)"
fi

echo "📝 Test 9: PUT /products/1/stock avec token gestionnaire (doit réussir)"
RESPONSE=$(curl -s -X PUT "$BASE_URL/products/1/stock" \
  -H "Authorization: Bearer $GESTIONNAIRE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": 100}' \
  -w "%{http_code}")

HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "200" ]; then
  echo "✅ Gestionnaire peut mettre à jour le stock (200)"
else
  echo "❌ Gestionnaire ne peut pas mettre à jour le stock ($HTTP_CODE)"
fi

echo ""
echo "🎯 Tests d'authentification sans token"
echo "======================================"

# Test 10: Accès sans token (doit échouer)
echo "📝 Test 10: GET /products sans token (doit échouer)"
RESPONSE=$(curl -s -X GET "$BASE_URL/products" \
  -w "%{http_code}")

HTTP_CODE="${RESPONSE: -3}"
if [ "$HTTP_CODE" = "401" ]; then
  echo "✅ Accès refusé sans token (401 - Non autorisé)"
else
  echo "❌ Accès autorisé sans token ($HTTP_CODE)"
fi

echo ""
echo "🏁 Tests terminés!"
echo "===================="
