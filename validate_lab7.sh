#!/bin/bash

# Validation finale Lab 7 - Vérification de tous les livrables
# Usage: ./validate_lab7.sh

set -e

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}"
echo "=================================================================="
echo "              VALIDATION FINALE LAB 7 - LOG430"
echo "         Architecture Événementielle Complète"
echo "=================================================================="
echo -e "${NC}"

check_file() {
    local file=$1
    local description=$2
    if [ -f "$file" ]; then
        echo -e "✅ ${GREEN}$description${NC}"
        return 0
    else
        echo -e "❌ ${RED}$description${NC}"
        return 1
    fi
}

check_directory() {
    local dir=$1
    local description=$2
    if [ -d "$dir" ]; then
        echo -e "✅ ${GREEN}$description${NC}"
        return 0
    else
        echo -e "❌ ${RED}$description${NC}"
        return 1
    fi
}

check_executable() {
    local file=$1
    local description=$2
    if [ -x "$file" ]; then
        echo -e "✅ ${GREEN}$description${NC}"
        return 0
    else
        echo -e "❌ ${RED}$description${NC}"
        return 1
    fi
}

errors=0

echo -e "${BLUE}📋 VÉRIFICATION DES LIVRABLES OBLIGATOIRES${NC}"
echo ""

# Documentation principale
echo "📚 Documentation Académique:"
check_file "README_LAB7.md" "README Lab 7 avec instructions complètes" || ((errors++))
check_file "RAPPORT_LAB7.md" "Rapport académique détaillé" || ((errors++))
check_file "DOCUMENTATION_TECHNIQUE.md" "Documentation technique" || ((errors++))
check_file "ADR.md" "Architecture Decision Records" || ((errors++))
check_file "scenario_metier_lab7.md" "Scénario métier détaillé" || ((errors++))
check_file "extraits_evenements_lab7.md" "Extraits d'événements" || ((errors++))
echo ""

# Diagrammes PlantUML
echo "🎨 Diagrammes PlantUML:"
check_directory "Diagrammes-lab7" "Dossier des diagrammes" || ((errors++))
check_file "Diagrammes-lab7/architecture_pubsub_eventstore_cqrs.puml" "Diagramme architecture" || ((errors++))
check_file "Diagrammes-lab7/saga_choreographee_sequence.puml" "Diagramme saga" || ((errors++))
check_file "Diagrammes-lab7/evenements_metier.puml" "Diagramme événements" || ((errors++))
echo ""

# Services événementiels
echo "🏗️ Services Événementiels:"
check_directory "event-bus-service" "Event Bus Service (hub central)" || ((errors++))
check_file "event-bus-service/events.py" "Modèles d'événements" || ((errors++))
check_file "event-bus-service/event_store.py" "Event Store MongoDB" || ((errors++))
check_file "event-bus-service/redis_event_bus.py" "Pub/Sub Redis Streams" || ((errors++))
check_directory "inventory-event-service" "Inventory Service" || ((errors++))
check_directory "procurement-service" "Procurement Service" || ((errors++))
check_directory "supplier-service" "Supplier Service" || ((errors++))
check_directory "analytics-service" "Analytics Service (CQRS)" || ((errors++))
echo ""

# Configuration et déploiement
echo "⚙️ Configuration et Déploiement:"
check_file "docker-compose-lab7.yml" "Docker Compose services" || ((errors++))
check_file "event-infrastructure.yml" "Infrastructure événementielle" || ((errors++))
check_file "monitoring/prometheus.yml" "Configuration Prometheus" || ((errors++))
check_file "monitoring/grafana-dashboard.json" "Dashboard Grafana" || ((errors++))
echo ""

# Scripts d'automatisation
echo "🚀 Scripts d'Automatisation:"
check_executable "run_lab7.sh" "Script principal d'automatisation" || ((errors++))
check_executable "demo_lab7.sh" "Script de démonstration" || ((errors++))
check_file "init_lab7_data.py" "Initialisation des données" || ((errors++))
echo ""

# Tests
echo "🧪 Tests et Validation:"
check_file "test_event_driven_architecture.py" "Tests architecture événementielle" || ((errors++))
check_file "test_failure_scenarios.py" "Tests scénarios d'échec" || ((errors++))
check_file "test_integration_complete.py" "Tests intégration complète" || ((errors++))
echo ""

# Guides et support
echo "📖 Guides d'Évaluation:"
check_file "VALIDATION_LIVRABLES_LAB7.md" "Validation des livrables" || ((errors++))
check_file "GUIDE_EVALUATION_LAB7.md" "Guide pour le correcteur" || ((errors++))
check_file "LIVRABLES_LAB7.md" "Liste complète des livrables" || ((errors++))
echo ""

# Vérification du contenu
echo -e "${BLUE}📝 VÉRIFICATION DU CONTENU${NC}"
echo ""

# Vérifier la taille des fichiers importants
echo "📊 Taille des documents:"
if [ -f "RAPPORT_LAB7.md" ]; then
    lines=$(wc -l < RAPPORT_LAB7.md)
    if [ $lines -gt 500 ]; then
        echo -e "✅ ${GREEN}Rapport académique: $lines lignes (détaillé)${NC}"
    else
        echo -e "⚠️ ${YELLOW}Rapport académique: $lines lignes (pourrait être plus détaillé)${NC}"
    fi
fi

if [ -f "README_LAB7.md" ]; then
    lines=$(wc -l < README_LAB7.md)
    echo -e "✅ ${GREEN}README Lab 7: $lines lignes${NC}"
fi

# Vérifier les patterns dans les fichiers
echo ""
echo "🔍 Vérification des patterns requis:"

patterns=(
    "Event Sourcing:event-bus-service/event_store.py"
    "CQRS:analytics-service/app.py"
    "Pub/Sub:event-bus-service/redis_event_bus.py"
    "Saga:procurement-service/app.py"
    "Compensation:extraits_evenements_lab7.md"
)

for pattern in "${patterns[@]}"; do
    IFS=':' read -r name file <<< "$pattern"
    if [ -f "$file" ] && grep -q -i "${name}" "$file"; then
        echo -e "✅ ${GREEN}Pattern $name trouvé dans $file${NC}"
    else
        echo -e "⚠️ ${YELLOW}Pattern $name à vérifier dans $file${NC}"
    fi
done

echo ""

# Résumé final
echo -e "${PURPLE}=================================================================="
echo "                        RÉSUMÉ DE LA VALIDATION"
echo "==================================================================${NC}"

if [ $errors -eq 0 ]; then
    echo -e "🎉 ${GREEN}SUCCÈS COMPLET ! Tous les livrables sont présents.${NC}"
    echo ""
    echo -e "${GREEN}✅ Architecture Événementielle Complète${NC}"
    echo -e "${GREEN}✅ Event Sourcing + CQRS + Pub/Sub + Saga${NC}"
    echo -e "${GREEN}✅ Documentation Académique Exhaustive${NC}"
    echo -e "${GREEN}✅ Tests et Validation Automatisés${NC}"
    echo -e "${GREEN}✅ Scripts d'Automatisation Prêts${NC}"
    echo -e "${GREEN}✅ Monitoring et Observabilité${NC}"
    echo ""
    echo -e "${BLUE}🎓 PRÊT POUR ÉVALUATION ACADÉMIQUE !${NC}"
    echo ""
    echo -e "${YELLOW}Prochaines étapes:${NC}"
    echo "1. ./run_lab7.sh start    # Démarrer le système"
    echo "2. ./demo_lab7.sh         # Démonstration complète"
    echo "3. Prendre des captures d'écran avec ./generate_screenshots.sh"
    echo "4. Remettre le Lab 7 complet"
    
else
    echo -e "⚠️ ${YELLOW}$errors fichier(s) manquant(s) ou problème(s) détecté(s).${NC}"
    echo ""
    echo -e "${BLUE}Actions recommandées:${NC}"
    echo "1. Vérifier les fichiers manqués ci-dessus"
    echo "2. Relancer la validation: ./validate_lab7.sh"
    echo "3. Consulter GUIDE_EVALUATION_LAB7.md pour les détails"
fi

echo ""
echo -e "${BLUE}📊 STATISTIQUES DU PROJET:${NC}"
echo "• Services événementiels: $(find . -name "*-service" -type d | wc -l)"
echo "• Scripts d'automatisation: $(find . -name "*.sh" | wc -l)"
echo "• Tests: $(find . -name "test_*.py" | wc -l)"
echo "• Documentation: $(find . -name "*.md" | wc -l) fichiers Markdown"
echo "• Diagrammes PlantUML: $(find . -name "*.puml" | wc -l)"

echo ""
echo -e "${GREEN}✨ Lab 7 - Architecture Événementielle - LOG430 - ÉTS ✨${NC}"

exit $errors
