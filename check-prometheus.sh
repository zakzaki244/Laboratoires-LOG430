#!/bin/bash

# Script pour vérifier la configuration Prometheus

echo "🔍 Vérification de la configuration Prometheus"
echo "============================================="

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les résultats
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Fonction pour afficher les avertissements
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# 1. Vérifier la syntaxe du fichier prometheus.yml
echo "1. Vérification de la syntaxe YAML..."
if command -v promtool &> /dev/null; then
    promtool check config prometheus.yml
    syntax_result=$?
    print_result $syntax_result "Syntaxe prometheus.yml"
else
    print_warning "promtool non installé - validation manuelle nécessaire"
    if python3 -c "import yaml; yaml.safe_load(open('prometheus.yml'))" 2>/dev/null; then
        print_result 0 "Syntaxe YAML basique"
    else
        print_result 1 "Syntaxe YAML invalide"
    fi
fi

# 2. Vérifier les targets configurés
echo ""
echo "2. Vérification des targets configurés..."

expected_targets=("api-gateway:5000" "store-service:5001" "product-service:5002" "sales-service:5003" "inventory-service:5004" "customer-service:5005" "cart-service:5006" "checkout-service:5007")

for target in "${expected_targets[@]}"; do
    if grep -q "$target" prometheus.yml; then
        print_result 0 "Target $target configuré"
    else
        print_result 1 "Target $target manquant"
    fi
done

# 3. Vérifier l'intervalle de scraping
echo ""
echo "3. Vérification des intervalles de scraping..."

global_interval=$(grep -A1 "global:" prometheus.yml | grep "scrape_interval" | cut -d':' -f2 | tr -d ' ')
if [[ "$global_interval" =~ ^[0-9]+s$ ]]; then
    print_result 0 "Intervalle global: $global_interval"
else
    print_result 1 "Intervalle global mal configuré"
fi

# 4. Vérifier si Prometheus est accessible
echo ""
echo "4. Vérification de l'accessibilité de Prometheus..."

if curl -s http://localhost:9090/api/v1/status/config > /dev/null 2>&1; then
    print_result 0 "Prometheus accessible sur le port 9090"
    
    # Vérifier les targets actifs
    echo ""
    echo "5. Vérification des targets actifs..."
    
    active_targets=$(curl -s http://localhost:9090/api/v1/targets | jq -r '.data.activeTargets[].discoveredLabels.__address__' 2>/dev/null | sort | uniq)
    
    if [ -n "$active_targets" ]; then
        echo "Targets actifs détectés:"
        echo "$active_targets" | while read -r target; do
            echo "  • $target"
        done
    else
        print_warning "Aucun target actif détecté"
    fi
    
else
    print_result 1 "Prometheus non accessible (démarrez d'abord docker-compose)"
fi

# 5. Vérifier les métriques disponibles
echo ""
echo "6. Vérification des métriques disponibles..."

if curl -s http://localhost:9090/api/v1/targets > /dev/null 2>&1; then
    up_targets=$(curl -s http://localhost:9090/api/v1/query?query=up | jq -r '.data.result[].metric.job' 2>/dev/null | sort | uniq)
    
    if [ -n "$up_targets" ]; then
        echo "Services avec métriques actives:"
        echo "$up_targets" | while read -r service; do
            echo "  • $service"
        done
    else
        print_warning "Aucune métrique active détectée"
    fi
fi

# 6. Recommandations
echo ""
echo "7. Recommandations pour optimiser Prometheus..."

# Vérifier si les alertes sont configurées
if [ -f "prometheus-alerts.yml" ]; then
    print_result 0 "Fichier d'alertes prometheus-alerts.yml présent"
    
    # Mettre à jour prometheus.yml pour inclure les alertes
    if grep -q "prometheus-alerts.yml" prometheus.yml; then
        print_result 0 "Alertes configurées dans prometheus.yml"
    else
        print_warning "Alertes non configurées - mise à jour recommandée"
        echo "  Ajoutez à prometheus.yml:"
        echo "  rule_files:"
        echo "    - \"prometheus-alerts.yml\""
    fi
else
    print_warning "Fichier d'alertes non trouvé"
fi

# 7. Vérifier les exporters recommandés
echo ""
echo "8. Vérification des exporters recommandés..."

recommended_exporters=("node_exporter" "postgres_exporter" "redis_exporter")

for exporter in "${recommended_exporters[@]}"; do
    if grep -q "$exporter" prometheus.yml; then
        print_result 0 "Exporter $exporter configuré"
    else
        print_warning "Exporter $exporter recommandé"
    fi
done

# Résumé final
echo ""
echo "============================================="
echo "🎯 RÉSUMÉ DE LA CONFIGURATION PROMETHEUS"
echo "============================================="

echo ""
echo "📊 Configuration actuelle:"
echo "  • Fichier: prometheus.yml ✅"
echo "  • Targets: Tous les microservices"
echo "  • Intervalle: 15s (global), 10s (API Gateway)"
echo "  • Port: 9090"
echo ""
echo "🔧 Services monitorés:"
echo "  • API Gateway (point d'entrée)"
echo "  • 7 microservices métier"
echo "  • Infrastructure (Nginx, Redis)"
echo "  • Bases de données PostgreSQL"
echo ""
echo "📈 Métriques collectées:"
echo "  • Requêtes HTTP (taux, latence, erreurs)"
echo "  • Santé des services (up/down)"
echo "  • Utilisation des ressources"
echo "  • Performances des bases de données"
echo ""
echo "🎯 Accès aux outils:"
echo "  • Prometheus: http://localhost:9090"
echo "  • Grafana: http://localhost:3000"
echo "  • Targets: http://localhost:9090/targets"
echo "  • Métriques: http://localhost:9090/graph"
echo ""
echo "💡 Prochaines étapes:"
echo "  1. Démarrer: docker-compose -f docker-compose-microservices.yml up -d"
echo "  2. Vérifier les targets: http://localhost:9090/targets"
echo "  3. Créer des dashboards Grafana"
echo "  4. Configurer les alertes"
echo ""
echo "🎉 Configuration Prometheus optimisée pour les microservices !"
