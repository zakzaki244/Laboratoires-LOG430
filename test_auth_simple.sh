#!/bin/bash

# Test simplifié de l'authentification JWT et des permissions produit
# LOG430 - Laboratoire - Système d'authentification microservices

echo "🔐 Test d'authentification JWT - Product Service"
echo "================================================"

# Configuration
CUSTOMER_SERVICE_URL="http://localhost:5005"
PRODUCT_SERVICE_URL="http://localhost:5002"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "\n${YELLOW}🔑 Test 1: Authentification Responsable Produit${NC}"
RESP_RESPONSE=$(curl -s -X POST $CUSTOMER_SERVICE_URL/api/customers/login \
    -H "Content-Type: application/json" \
    -d '{"email": "responsable.produit@supermarcher.com", "password": "produit123"}')

if echo "$RESP_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Authentification responsable produit réussie${NC}"
    RESP_TOKEN=$(echo "$RESP_RESPONSE" | jq -r '.access_token')
    
    echo -e "\n${YELLOW}📋 Test 2: Accès GET /products avec responsable produit${NC}"
    PRODUCTS_RESPONSE=$(curl -s -X GET $PRODUCT_SERVICE_URL/products \
        -H "Authorization: Bearer $RESP_TOKEN")
    
    if echo "$PRODUCTS_RESPONSE" | grep -q "Bananes"; then
        echo -e "${GREEN}✓ Accès aux produits autorisé${NC}"
        PRODUCT_COUNT=$(echo "$PRODUCTS_RESPONSE" | jq '. | length')
        echo "   Nombre de produits: $PRODUCT_COUNT"
    else
        echo -e "${RED}✗ Accès aux produits refusé${NC}"
    fi
    
    echo -e "\n${YELLOW}➕ Test 3: Création de produit avec responsable produit${NC}"
    CREATE_RESPONSE=$(curl -s -X POST $PRODUCT_SERVICE_URL/products \
        -H "Authorization: Bearer $RESP_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Product Auth", "price": 9.99, "category": "Test", "stock": 10, "store_id": 1}')
    
    if echo "$CREATE_RESPONSE" | grep -q "Test Product Auth"; then
        echo -e "${GREEN}✓ Création de produit autorisée${NC}"
        PRODUCT_ID=$(echo "$CREATE_RESPONSE" | jq -r '.id')
        echo "   Produit créé ID: $PRODUCT_ID"
    else
        echo -e "${RED}✗ Création de produit refusée${NC}"
        echo "   Réponse: $CREATE_RESPONSE"
    fi
    
else
    echo -e "${RED}✗ Authentification responsable produit échouée${NC}"
    echo "   Réponse: $RESP_RESPONSE"
fi

echo -e "\n${YELLOW}🔑 Test 4: Authentification Client${NC}"
CLIENT_RESPONSE=$(curl -s -X POST $CUSTOMER_SERVICE_URL/api/customers/login \
    -H "Content-Type: application/json" \
    -d '{"email": "client@supermarcher.com", "password": "client123"}')

if echo "$CLIENT_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Authentification client réussie${NC}"
    CLIENT_TOKEN=$(echo "$CLIENT_RESPONSE" | jq -r '.access_token')
    
    echo -e "\n${YELLOW}📋 Test 5: Accès GET /products avec client${NC}"
    CLIENT_PRODUCTS_RESPONSE=$(curl -s -X GET $PRODUCT_SERVICE_URL/products \
        -H "Authorization: Bearer $CLIENT_TOKEN")
    
    if echo "$CLIENT_PRODUCTS_RESPONSE" | grep -q "Bananes"; then
        echo -e "${GREEN}✓ Accès aux produits autorisé pour client${NC}"
    else
        echo -e "${RED}✗ Accès aux produits refusé pour client${NC}"
    fi
    
    echo -e "\n${YELLOW}➕ Test 6: Tentative création de produit avec client${NC}"
    CLIENT_CREATE_RESPONSE=$(curl -s -X POST $PRODUCT_SERVICE_URL/products \
        -H "Authorization: Bearer $CLIENT_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Client Product", "price": 5.99, "category": "Test", "stock": 5, "store_id": 1}')
    
    if echo "$CLIENT_CREATE_RESPONSE" | grep -q "Permissions insuffisantes"; then
        echo -e "${GREEN}✓ Création de produit correctement refusée pour client${NC}"
    else
        echo -e "${RED}✗ Création de produit autorisée pour client (erreur de sécurité)${NC}"
        echo "   Réponse: $CLIENT_CREATE_RESPONSE"
    fi
    
else
    echo -e "${RED}✗ Authentification client échouée${NC}"
    echo "   Réponse: $CLIENT_RESPONSE"
fi

echo -e "\n${YELLOW}🔑 Test 7: Authentification Gestionnaire${NC}"
GEST_RESPONSE=$(curl -s -X POST $CUSTOMER_SERVICE_URL/api/customers/login \
    -H "Content-Type: application/json" \
    -d '{"email": "gestionnaire@supermarcher.com", "password": "gestionnaire123"}')

if echo "$GEST_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓ Authentification gestionnaire réussie${NC}"
    GEST_TOKEN=$(echo "$GEST_RESPONSE" | jq -r '.access_token')
    
    echo -e "\n${YELLOW}📦 Test 8: Modification stock avec gestionnaire${NC}"
    STOCK_RESPONSE=$(curl -s -X PUT $PRODUCT_SERVICE_URL/products/1/stock \
        -H "Authorization: Bearer $GEST_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"quantity": 100}')
    
    if echo "$STOCK_RESPONSE" | grep -q "stock"; then
        echo -e "${GREEN}✓ Modification stock autorisée pour gestionnaire${NC}"
        NEW_STOCK=$(echo "$STOCK_RESPONSE" | jq -r '.stock')
        echo "   Nouveau stock: $NEW_STOCK"
    else
        echo -e "${RED}✗ Modification stock refusée pour gestionnaire${NC}"
        echo "   Réponse: $STOCK_RESPONSE"
    fi
    
else
    echo -e "${RED}✗ Authentification gestionnaire échouée${NC}"
    echo "   Réponse: $GEST_RESPONSE"
fi

echo -e "\n${YELLOW}🚫 Test 9: Accès sans token${NC}"
NO_TOKEN_RESPONSE=$(curl -s -X GET $PRODUCT_SERVICE_URL/products)

if echo "$NO_TOKEN_RESPONSE" | grep -q "Token JWT manquant"; then
    echo -e "${GREEN}✓ Accès sans token correctement refusé${NC}"
else
    echo -e "${RED}✗ Accès sans token autorisé (erreur de sécurité)${NC}"
    echo "   Réponse: $NO_TOKEN_RESPONSE"
fi

echo -e "\n${GREEN}✅ Tests terminés${NC}"
echo "================================================"
