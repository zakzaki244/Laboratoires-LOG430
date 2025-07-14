#!/bin/bash

# Test simple de connexion qui suit les redirections

echo "=== TEST DE CONNEXION VIA INTERFACE WEB ==="

echo "Test avec gestionnaire / gestionnaire123:"
curl -L -c cookies.txt -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=gestionnaire&password=gestionnaire123" \
  http://localhost:5000/login | grep -o "Connexion réussie\|gestionnaire\|admin\|Marie\|Dupont"

echo -e "\n\nTest avec admin / admin123:"
curl -L -c cookies.txt -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123" \
  http://localhost:5000/login | grep -o "Connexion réussie\|admin\|Marie\|Dupont"

echo -e "\n\nTest avec employe / employe123:"
curl -L -c cookies.txt -X POST -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=employe&password=employe123" \
  http://localhost:5000/login | grep -o "Connexion réussie\|employe\|Jean\|Martin"

echo -e "\n\n=== TEST TERMINÉ ==="
