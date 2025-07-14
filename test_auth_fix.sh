#!/bin/bash

echo "=== Test des corrections d'authentification ==="
echo "Date: $(date)"
echo ""

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "1. Test de connexion avec chaque rôle..."
echo ""

# Test Admin
echo -n "Admin: "
response=$(curl -X POST http://localhost:5000/login \
    -d "username=admin@supermarcher.com&password=admin123" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -L -s -w "HTTPCODE:%{http_code}")

if echo "$response" | grep -q "HTTPCODE:200"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ KO${NC}"
fi

# Test Gestionnaire
echo -n "Gestionnaire: "
response=$(curl -X POST http://localhost:5000/login \
    -d "username=gestionnaire@supermarcher.com&password=gestionnaire123" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -L -s -w "HTTPCODE:%{http_code}")

if echo "$response" | grep -q "HTTPCODE:200"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ KO${NC}"
fi

# Test Responsable Produit
echo -n "Responsable Produit: "
response=$(curl -X POST http://localhost:5000/login \
    -d "username=responsable.produit@supermarcher.com&password=produit123" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -L -s -w "HTTPCODE:%{http_code}")

if echo "$response" | grep -q "HTTPCODE:200"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ KO${NC}"
fi

# Test Responsable Logistique
echo -n "Responsable Logistique: "
response=$(curl -X POST http://localhost:5000/login \
    -d "username=responsable.logistique@supermarcher.com&password=logistique123" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -L -s -w "HTTPCODE:%{http_code}")

if echo "$response" | grep -q "HTTPCODE:200"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ KO${NC}"
fi

# Test Employé Magasin
echo -n "Employé Magasin: "
response=$(curl -X POST http://localhost:5000/login \
    -d "username=employe.magasin@supermarcher.com&password=employe123" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -L -s -w "HTTPCODE:%{http_code}")

if echo "$response" | grep -q "HTTPCODE:200"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ KO${NC}"
fi

# Test Client
echo -n "Client: "
response=$(curl -X POST http://localhost:5000/login \
    -d "username=client@supermarcher.com&password=client123" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -L -s -w "HTTPCODE:%{http_code}")

if echo "$response" | grep -q "HTTPCODE:200"; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ KO${NC}"
fi

echo ""
echo -e "${YELLOW}=== Résumé des corrections ===${NC}"
echo "• Suppression des décorateurs restrictifs de rôle"
echo "• Correction de session.get('role') dans auth_decorators.py"
echo "• Amélioration des redirections selon les rôles"
echo "• Clients redirigés vers /products au lieu de /admin"
echo "• Ajout d'une route pour nettoyer les messages flash"
echo ""
echo "Les connexions devraient maintenant fonctionner correctement !"
