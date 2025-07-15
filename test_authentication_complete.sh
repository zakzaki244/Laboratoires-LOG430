#!/bin/bash

# Test complet de l'authentification JWT et des permissions produit
# LOG430 - Laboratoire - Système d'authentification microservices

echo "🔐 Test d'authentification et d'autorisation JWT - Product Service"
echo "=================================================================="

# Configuration
CUSTOMER_SERVICE_URL="http://localhost:5005"
PRODUCT_SERVICE_URL="http://localhost:5002"

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ $2${NC}"
    else
        echo -e "${RED}✗ $2${NC}"
    fi
}

# Fonction pour tester l'authentification
test_authentication() {
    local email=$1
    local password=$2
    local role=$3
    
    echo -e "\n${YELLOW}🔑 Test d'authentification : $email ($role)${NC}"
    
    response=$(curl -s -X POST $CUSTOMER_SERVICE_URL/api/customers/login \
        -H "Content-Type: application/json" \
        -d "{\"email\": \"$email\", \"password\": \"$password\"}")
    
    if echo "$response" | grep -q "access_token"; then
        token=$(echo "$response" | jq -r '.access_token')
        print_result 0 "Authentification réussie"
        echo "$token"
    else
        print_result 1 "Échec de l'authentification"
        echo "$response"
        echo ""
    fi
}

# Fonction pour tester l'accès GET aux produits
test_get_products() {
    local token=$1
    local role=$2
    
    echo -e "\n${YELLOW}📋 Test GET /products avec le rôle $role${NC}"
    
    response=$(curl -s -w "HTTP_STATUS:%{http_code}" \
        -X GET $PRODUCT_SERVICE_URL/products \
        -H "Authorization: Bearer $token")
    
    http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    if [ "$http_code" -eq 200 ]; then
        product_count=$(echo "$body" | jq '. | length')
        print_result 0 "Accès autorisé - $product_count produits trouvés"
    else
        print_result 1 "Accès refusé - Code HTTP: $http_code"
        echo "$body"
    fi
}

# Fonction pour tester la création de produits
test_create_product() {
    local token=$1
    local role=$2
    
    echo -e "\n${YELLOW}➕ Test POST /products avec le rôle $role${NC}"
    
    response=$(curl -s -w "HTTP_STATUS:%{http_code}" \
        -X POST $PRODUCT_SERVICE_URL/products \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d '{"name": "Test Product '"$role"'", "price": 9.99, "category": "Test", "stock": 10, "store_id": 1}')
    
    http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    if [ "$http_code" -eq 201 ] || [ "$http_code" -eq 200 ]; then
        product_id=$(echo "$body" | jq -r '.id // empty')
        print_result 0 "Création autorisée - Produit ID: $product_id"
        echo "$product_id"
    else
        print_result 1 "Création refusée - Code HTTP: $http_code"
        echo "$body"
        echo ""
    fi
}

# Fonction pour tester la modification du stock
test_update_stock() {
    local token=$1
    local role=$2
    local product_id=$3
    
    echo -e "\n${YELLOW}📦 Test PUT /products/$product_id/stock avec le rôle $role${NC}"
    
    response=$(curl -s -w "HTTP_STATUS:%{http_code}" \
        -X PUT $PRODUCT_SERVICE_URL/products/$product_id/stock \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d '{"quantity": 50}')
    
    http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    if [ "$http_code" -eq 200 ]; then
        new_stock=$(echo "$body" | jq -r '.stock // empty')
        print_result 0 "Modification autorisée - Nouveau stock: $new_stock"
    else
        print_result 1 "Modification refusée - Code HTTP: $http_code"
        echo "$body"
    fi
}

# Fonction pour tester l'accès sans token
test_no_token() {
    echo -e "\n${YELLOW}🚫 Test d'accès sans token${NC}"
    
    response=$(curl -s -w "HTTP_STATUS:%{http_code}" \
        -X GET $PRODUCT_SERVICE_URL/products)
    
    http_code=$(echo "$response" | grep -o "HTTP_STATUS:[0-9]*" | cut -d: -f2)
    body=$(echo "$response" | sed 's/HTTP_STATUS:[0-9]*$//')
    
    if [ "$http_code" -eq 401 ]; then
        print_result 0 "Accès correctement refusé"
    else
        print_result 1 "Accès autorisé (erreur de sécurité) - Code HTTP: $http_code"
        echo "$body"
    fi
}

# Démarrage des tests
echo -e "\n${YELLOW}🚀 Démarrage des tests...${NC}"

# Test d'accès sans token
test_no_token

# Tests avec différents utilisateurs
echo -e "\n${YELLOW}=== Tests avec Admin ===${NC}"
ADMIN_TOKEN=$(test_authentication "admin@supermarcher.com" "admin123" "admin")
if [ -n "$ADMIN_TOKEN" ] && [ "$ADMIN_TOKEN" != "" ]; then
    test_get_products "$ADMIN_TOKEN" "admin"
    ADMIN_PRODUCT_ID=$(test_create_product "$ADMIN_TOKEN" "admin")
    if [ -n "$ADMIN_PRODUCT_ID" ] && [ "$ADMIN_PRODUCT_ID" != "" ]; then
        test_update_stock "$ADMIN_TOKEN" "admin" "$ADMIN_PRODUCT_ID"
    fi
fi

echo -e "\n${YELLOW}=== Tests avec Gestionnaire ===${NC}"
GEST_TOKEN=$(test_authentication "gestionnaire@supermarcher.com" "gestionnaire123" "gestionnaire")
if [ -n "$GEST_TOKEN" ] && [ "$GEST_TOKEN" != "" ]; then
    test_get_products "$GEST_TOKEN" "gestionnaire"
    GEST_PRODUCT_ID=$(test_create_product "$GEST_TOKEN" "gestionnaire")
    if [ -n "$GEST_PRODUCT_ID" ] && [ "$GEST_PRODUCT_ID" != "" ]; then
        test_update_stock "$GEST_TOKEN" "gestionnaire" "$GEST_PRODUCT_ID"
    fi
fi

echo -e "\n${YELLOW}=== Tests avec Responsable Produit ===${NC}"
RESP_TOKEN=$(test_authentication "responsable.produit@supermarcher.com" "produit123" "responsable_produit")
if [ -n "$RESP_TOKEN" ] && [ "$RESP_TOKEN" != "" ]; then
    test_get_products "$RESP_TOKEN" "responsable_produit"
    RESP_PRODUCT_ID=$(test_create_product "$RESP_TOKEN" "responsable_produit")
    if [ -n "$RESP_PRODUCT_ID" ] && [ "$RESP_PRODUCT_ID" != "" ]; then
        test_update_stock "$RESP_TOKEN" "responsable_produit" "$RESP_PRODUCT_ID"
    fi
fi

echo -e "\n${YELLOW}=== Tests avec Client ===${NC}"
CLIENT_TOKEN=$(test_authentication "client@supermarcher.com" "client123" "client")
if [ -n "$CLIENT_TOKEN" ] && [ "$CLIENT_TOKEN" != "" ]; then
    test_get_products "$CLIENT_TOKEN" "client"
    CLIENT_PRODUCT_ID=$(test_create_product "$CLIENT_TOKEN" "client")
    if [ -n "$CLIENT_PRODUCT_ID" ] && [ "$CLIENT_PRODUCT_ID" != "" ]; then
        test_update_stock "$CLIENT_TOKEN" "client" "$CLIENT_PRODUCT_ID"
    fi
fi

echo -e "\n${GREEN}✅ Tests terminés${NC}"
echo "=================================================================="
