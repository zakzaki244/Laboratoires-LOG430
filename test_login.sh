#!/bin/bash

# Script de test de connexion

echo "=== TEST DE CONNEXION ==="

echo "1. Test direct sur customer-service:"
curl -X POST -H "Content-Type: application/json" -H "Authorization: Bearer Supermarcher22102002" \
  -d '{"email": "gestionnaire@maisonmere.com", "password": "gestionnaire123"}' \
  http://localhost:5005/api/customers/login

echo -e "\n\n2. Test via API Gateway avec formulaire:"
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=gestionnaire&password=gestionnaire123" \
  http://localhost:5000/login | grep -o "Connexion réussie\|Nom d'utilisateur ou mot de passe incorrect\|Erreur de connexion"

echo -e "\n\n3. Test via API Gateway avec admin:"
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  http://localhost:5000/login | grep -o "Connexion réussie\|Nom d'utilisateur ou mot de passe incorrect\|Erreur de connexion"

echo -e "\n\n4. Test via API Gateway avec employe:"
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=employe&password=employe123" \
  http://localhost:5000/login | grep -o "Connexion réussie\|Nom d'utilisateur ou mot de passe incorrect\|Erreur de connexion"

echo -e "\n\n5. Test via API Gateway avec client1:"
curl -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=client1&password=client123" \
  http://localhost:5000/login | grep -o "Connexion réussie\|Nom d'utilisateur ou mot de passe incorrect\|Erreur de connexion"

echo -e "\n\n=== TEST TERMINÉ ===\n"
