#!/bin/bash

echo "=== TEST COMPLET DU SYSTÈME APRÈS REDÉMARRAGE ==="
echo "$(date)"
echo

# Configuration
API_TOKEN="Supermarcher22102002"
BASE_URL="http://10.194.32.174"

echo "1. VÉRIFICATION DE L'ÉTAT DES CONTENEURS"
echo "==========================================="
docker-compose -f docker-compose-microservices.yml ps
echo

echo "2. VÉRIFICATION DE LA SANTÉ DES SERVICES"
echo "========================================="
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
    name=$(echo $service | cut -d: -f1)
    port=$(echo $service | cut -d: -f2)
    echo -n "Testing $name... "
    response=$(curl -s -w "%{http_code}" "$BASE_URL:$port/health" -o /dev/null)
    if [ "$response" = "200" ]; then
        echo "✅ OK"
    else
        echo "❌ FAILED (HTTP $response)"
    fi
done
echo

echo "3. VÉRIFICATION DES DONNÉES - CUSTOMERS"
echo "======================================="
echo "Nombre de clients:"
customers_count=$(curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL:5005/api/customers" | jq '.customers | length' 2>/dev/null)
echo "✅ $customers_count clients trouvés"

echo "Liste des clients par rôle:"
curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL:5005/api/customers" | jq '.customers[] | {id, email, role, first_name, last_name}' 2>/dev/null || echo "❌ Erreur customers"
echo

echo "4. VÉRIFICATION DES DONNÉES - STORES"
echo "====================================="
echo "Nombre de magasins:"
stores_count=$(curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL:5001/stores" | jq '. | length' 2>/dev/null)
echo "✅ $stores_count magasins trouvés"

echo "Liste des magasins:"
curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL:5001/stores" | jq '.[] | {id, name, address, phone}' 2>/dev/null || echo "❌ Erreur stores"
echo

echo "5. VÉRIFICATION DES DONNÉES - PRODUCTS"
echo "======================================="
echo "Nombre de produits:"
products_count=$(curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL:5002/products" | jq '. | length' 2>/dev/null)
echo "✅ $products_count produits trouvés"

echo "Produits par magasin:"
for store_id in 1 2 3; do
    echo "Magasin $store_id:"
    curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL:5002/products?store_id=$store_id" | jq '.[] | {id, name, price, stock, category}' 2>/dev/null || echo "❌ Erreur produits magasin $store_id"
done
echo

echo "6. VÉRIFICATION DES DONNÉES - INVENTORY"
echo "========================================"
echo "Nombre d'éléments d'inventaire:"
inventory_count=$(curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL:5004/inventory" | jq '. | length' 2>/dev/null)
echo "✅ $inventory_count éléments d'inventaire trouvés"

echo "Inventaire par magasin:"
for store_id in 1 2 3; do
    echo "Magasin $store_id:"
    curl -s -H "Authorization: Bearer $API_TOKEN" "$BASE_URL:5004/inventory?store_id=$store_id" | jq '.[] | {product_id, quantity, min_threshold, max_threshold}' 2>/dev/null || echo "❌ Erreur inventaire magasin $store_id"
done
echo

echo "7. TEST DE LOGIN"
echo "================="
echo "Test de connexion avec le gestionnaire:"
login_response=$(curl -s -X POST \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "gestionnaire@maisonmere.com", "password": "gestionnaire123"}' \
  "$BASE_URL:5005/api/customers/login")

if echo "$login_response" | jq -e '.message' >/dev/null 2>&1; then
    echo "✅ Login réussi"
    echo "$login_response" | jq .
else
    echo "❌ Login échoué"
    echo "$login_response"
fi
echo

echo "8. TEST DE L'API GATEWAY"
echo "========================"
echo "Test d'accès via l'API Gateway:"
gateway_response=$(curl -s "$BASE_URL:5000/health" 2>/dev/null)
if [ $? -eq 0 ]; then
    echo "✅ API Gateway accessible"
else
    echo "❌ API Gateway non accessible"
fi
echo

echo "9. VÉRIFICATION DES BASES DE DONNÉES"
echo "===================================="
echo "Connexions aux bases de données:"
dbs=("db-stores" "db-products" "db-sales" "db-inventory" "db-customers" "db-cart" "db-checkout")
for db in "${dbs[@]}"; do
    echo -n "Testing $db... "
    if docker-compose -f docker-compose-microservices.yml exec -T "$db" pg_isready -U log430 >/dev/null 2>&1; then
        echo "✅ OK"
    else
        echo "❌ FAILED"
    fi
done
echo

echo "=== RÉSUMÉ DES PARAMÈTRES DE CONNEXION ==="
echo "==========================================="
echo "API TOKEN: $API_TOKEN"
echo "Services disponibles:"
echo "  - API Gateway: http://10.194.32.174:5000"
echo "  - Store Service: http://10.194.32.174:5001"
echo "  - Product Service: http://10.194.32.174:5002"
echo "  - Sales Service: http://10.194.32.174:5003"
echo "  - Inventory Service: http://10.194.32.174:5004"
echo "  - Customer Service: http://10.194.32.174:5005"
echo "  - Cart Service: http://10.194.32.174:5006"
echo "  - Checkout Service: http://10.194.32.174:5007"
echo
echo "Comptes de test:"
echo "  - Gestionnaire: gestionnaire@maisonmere.com / gestionnaire123"
echo "  - Employé: employe@magasin1.com / employe123"
echo "  - Client 1: client1@test.com / client123"
echo "  - Client 2: client2@test.com / client123"
echo
echo "Bases de données PostgreSQL:"
echo "  - Customers DB: 10.194.32.174:5437 (log430/laboratoire)"
echo "  - Stores DB: 10.194.32.174:5433 (log430/laboratoire)"
echo "  - Products DB: 10.194.32.174:5434 (log430/laboratoire)"
echo "  - Sales DB: 10.194.32.174:5435 (log430/laboratoire)"
echo "  - Inventory DB: 10.194.32.174:5436 (log430/laboratoire)"
echo "  - Cart DB: 10.194.32.174:5438 (log430/laboratoire)"
echo "  - Checkout DB: 10.194.32.174:5439 (log430/laboratoire)"
echo
echo "=== TEST TERMINÉ ==="
