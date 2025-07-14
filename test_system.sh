#!/bin/bash

# Script de test du système complet E-Commerce

echo "🚀 Test du système E-Commerce avec architecture microservices"
echo "=============================================================="

# Configuration
API_TOKEN="Supermarcher22102002"
CUSTOMER_SERVICE="http://localhost:5005"
STORE_SERVICE="http://localhost:5001"
PRODUCT_SERVICE="http://localhost:5002"
API_GATEWAY="http://localhost:8080"

echo ""
echo "📋 Comptes utilisateurs disponibles :"
echo "- Gestionnaire Maison Mère : gestionnaire@maisonmere.com / gestionnaire123"
echo "- Employé Magasin : employe@magasin1.com / employe123"
echo "- Responsable Logistique : logistique@centre.com / logistique123"
echo "- Responsable Produit : produit@maisonmere.com / produit123"
echo "- Client 1 : client1@test.com / client123"
echo "- Client 2 : client2@test.com / client123"
echo ""

echo "🔍 Test 1 : Vérification du service Customer"
echo "---------------------------------------------"
response=$(curl -s -X GET "$CUSTOMER_SERVICE/api/customers" -H "Authorization: Bearer $API_TOKEN")
if [[ $response == *"customers"* ]]; then
    echo "✅ Service Customer fonctionne"
    echo "📊 Nombre d'utilisateurs : $(echo $response | jq '.customers | length')"
else
    echo "❌ Service Customer ne répond pas"
fi

echo ""
echo "🔍 Test 2 : Connexion Gestionnaire"
echo "-----------------------------------"
login_response=$(curl -s -X POST "$CUSTOMER_SERVICE/api/customers/login" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "gestionnaire@maisonmere.com", "password": "gestionnaire123"}')

if [[ $login_response == *"Connexion réussie"* ]]; then
    echo "✅ Connexion gestionnaire réussie"
    echo "👤 Utilisateur : $(echo $login_response | jq -r '.customer.first_name') $(echo $login_response | jq -r '.customer.last_name')"
    echo "🔑 Rôle : $(echo $login_response | jq -r '.customer.role')"
else
    echo "❌ Échec de la connexion gestionnaire"
fi

echo ""
echo "🔍 Test 3 : Connexion Employé Magasin"
echo "--------------------------------------"
employee_response=$(curl -s -X POST "$CUSTOMER_SERVICE/api/customers/login" \
  -H "Authorization: Bearer $API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"email": "employe@magasin1.com", "password": "employe123"}')

if [[ $employee_response == *"Connexion réussie"* ]]; then
    echo "✅ Connexion employé réussie"
    echo "👤 Utilisateur : $(echo $employee_response | jq -r '.customer.first_name') $(echo $employee_response | jq -r '.customer.last_name')"
    echo "🔑 Rôle : $(echo $employee_response | jq -r '.customer.role')"
    echo "🏪 Magasin : $(echo $employee_response | jq -r '.customer.store_id')"
else
    echo "❌ Échec de la connexion employé"
fi

echo ""
echo "🔍 Test 4 : Récupération par rôle"
echo "----------------------------------"
managers_response=$(curl -s -X GET "$CUSTOMER_SERVICE/api/customers/role/gestionnaire_maison_mere" \
  -H "Authorization: Bearer $API_TOKEN")

if [[ $managers_response == *"customers"* ]]; then
    echo "✅ Récupération des gestionnaires réussie"
    echo "📊 Nombre de gestionnaires : $(echo $managers_response | jq '.customers | length')"
else
    echo "❌ Échec de la récupération des gestionnaires"
fi

echo ""
echo "🔍 Test 5 : Vérification des services"
echo "-------------------------------------"
services=("customer-service:5005" "store-service:5001" "product-service:5002" "api-gateway:8080")

for service in "${services[@]}"; do
    name=$(echo $service | cut -d':' -f1)
    port=$(echo $service | cut -d':' -f2)
    
    if nc -z localhost $port 2>/dev/null; then
        echo "✅ $name est actif sur le port $port"
    else
        echo "❌ $name n'est pas actif sur le port $port"
    fi
done

echo ""
echo "🔍 Test 6 : Vérification des bases de données"
echo "----------------------------------------------"
databases=("customers:5437" "stores:5433" "products:5434" "sales:5435" "inventory:5436")

for db in "${databases[@]}"; do
    name=$(echo $db | cut -d':' -f1)
    port=$(echo $db | cut -d':' -f2)
    
    if nc -z localhost $port 2>/dev/null; then
        echo "✅ Base de données $name est active sur le port $port"
    else
        echo "❌ Base de données $name n'est pas active sur le port $port"
    fi
done

echo ""
echo "📋 Résumé des Use Cases implémentés :"
echo "======================================"
echo "✅ UC9 : Créer un compte client (système d'authentification)"
echo "✅ Administration : Interface pour gestionnaires/responsables"
echo "🔄 UC1 : Générer rapports (en cours)"
echo "🔄 UC2 : Consulter stock (en cours)"
echo "🔄 UC4 : Mettre à jour produits (en cours)"
echo "🔄 UC6 : Approvisionnement (en cours)"
echo "🔄 UC10-UC15 : Panier et commandes (en cours)"

echo ""
echo "🌐 Accès à l'interface web :"
echo "- Interface principale : http://localhost:8080"
echo "- Interface d'administration : http://localhost:8080/admin"
echo "- Connexion avec les comptes listés ci-dessus"

echo ""
echo "🎯 Prochaines étapes recommandées :"
echo "1. Lancer tous les services et bases de données"
echo "2. Tester l'interface web d'administration"
echo "3. Ajouter des magasins et produits via l'interface"
echo "4. Implémenter les use cases manquants"
