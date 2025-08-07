#!/bin/bash

# Script d'automatisation Lab 7 - Architecture Événementielle
# Usage: ./run_lab7.sh [command]

set -e

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
LAB7_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE_INFRA="event-infrastructure.yml"
COMPOSE_FILE_SERVICES="docker-compose-lab7.yml"

# Fonctions utilitaires
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérification des prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    # Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 n'est pas installé"
        exit 1
    fi
    
    log_success "Tous les prérequis sont satisfaits"
}

# Nettoyage complet
cleanup() {
    log_info "Nettoyage de l'environnement Lab 7..."
    
    # Arrêter tous les services
    docker-compose -f "$COMPOSE_FILE_SERVICES" down -v --remove-orphans 2>/dev/null || true
    docker-compose -f "$COMPOSE_FILE_INFRA" down -v --remove-orphans 2>/dev/null || true
    
    # Nettoyer les images Docker (optionnel)
    if [[ "$1" == "--full" ]]; then
        log_info "Nettoyage complet des images Docker..."
        docker system prune -f
        docker volume prune -f
    fi
    
    log_success "Nettoyage terminé"
}

# Démarrage de l'infrastructure
start_infrastructure() {
    log_info "Démarrage de l'infrastructure événementielle..."
    
    # Démarrer Redis et MongoDB
    docker-compose -f "$COMPOSE_FILE_INFRA" up -d
    
    # Attendre que les services soient prêts
    log_info "Attente de la disponibilité des services infrastructure..."
    sleep 10
    
    # Vérifier Redis
    if ! docker exec $(docker-compose -f "$COMPOSE_FILE_INFRA" ps -q redis) redis-cli ping > /dev/null 2>&1; then
        log_error "Redis n'est pas disponible"
        return 1
    fi
    
    # Vérifier MongoDB
    if ! docker exec $(docker-compose -f "$COMPOSE_FILE_INFRA" ps -q mongodb) mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        log_error "MongoDB n'est pas disponible"
        return 1
    fi
    
    log_success "Infrastructure démarrée avec succès"
}

# Démarrage des services
start_services() {
    log_info "Démarrage des services Lab 7..."
    
    # Construire et démarrer tous les services
    docker-compose -f "$COMPOSE_FILE_SERVICES" up -d --build
    
    # Attendre que les services soient prêts
    log_info "Attente de la disponibilité des services..."
    sleep 30
    
    # Vérifier la santé des services
    check_services_health
}

# Vérification de la santé des services
check_services_health() {
    log_info "Vérification de la santé des services..."
    
    services=(
        "http://localhost:5000/health:Event Bus Service"
        "http://localhost:5001/health:Inventory Service"
        "http://localhost:5002/health:Procurement Service"
        "http://localhost:5003/health:Supplier Service"
        "http://localhost:5007/health:Analytics Service"
    )
    
    all_healthy=true
    
    for service in "${services[@]}"; do
        IFS=':' read -r url name <<< "$service"
        if curl -f -s "$url" > /dev/null 2>&1; then
            log_success "$name: ✓ OK"
        else
            log_error "$name: ✗ FAILED"
            all_healthy=false
        fi
    done
    
    if $all_healthy; then
        log_success "Tous les services sont opérationnels"
        return 0
    else
        log_error "Certains services ne sont pas disponibles"
        return 1
    fi
}

# Initialisation des données
init_data() {
    log_info "Initialisation des données de test..."
    
    if [[ -f "init_lab7_data.py" ]]; then
        python3 init_lab7_data.py
        log_success "Données initialisées"
    else
        log_warning "Script d'initialisation non trouvé"
    fi
}

# Exécution des tests
run_tests() {
    log_info "Exécution des tests Lab 7..."
    
    # Tests d'architecture événementielle
    if [[ -f "test_event_driven_architecture.py" ]]; then
        log_info "Tests d'architecture événementielle..."
        python3 test_event_driven_architecture.py
    fi
    
    # Tests de scénarios d'échec
    if [[ -f "test_failure_scenarios.py" ]]; then
        log_info "Tests de scénarios d'échec..."
        python3 test_failure_scenarios.py
    fi
    
    # Tests d'intégration complète
    if [[ -f "test_integration_complete.py" ]]; then
        log_info "Tests d'intégration complète..."
        python3 test_integration_complete.py
    fi
    
    log_success "Tests terminés - vérifiez les rapports générés"
}

# Monitoring et logs
show_logs() {
    service_name="$1"
    
    if [[ -z "$service_name" ]]; then
        log_info "Affichage des logs de tous les services..."
        docker-compose -f "$COMPOSE_FILE_SERVICES" logs -f
    else
        log_info "Affichage des logs du service: $service_name"
        docker-compose -f "$COMPOSE_FILE_SERVICES" logs -f "$service_name"
    fi
}

# Monitoring en temps réel
monitor() {
    log_info "Monitoring en temps réel..."
    
    echo "=== Services Status ==="
    check_services_health
    
    echo -e "\n=== Docker Containers ==="
    docker-compose -f "$COMPOSE_FILE_SERVICES" ps
    
    echo -e "\n=== Resource Usage ==="
    docker stats --no-stream
    
    if command -v watch &> /dev/null; then
        log_info "Mode monitoring continu (Ctrl+C pour arrêter)..."
        watch -n 5 "curl -s http://localhost:5007/projections/dashboard | jq -r '.timestamp, .system_summary'"
    fi
}

# Aide
show_help() {
    echo "Script d'automatisation Lab 7 - Architecture Événementielle"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start           Démarrage complet (infrastructure + services + données)"
    echo "  stop            Arrêt de tous les services"
    echo "  restart         Redémarrage complet"
    echo "  cleanup         Nettoyage de l'environnement"
    echo "  cleanup --full  Nettoyage complet avec suppression des images"
    echo "  test            Exécution de tous les tests"
    echo "  health          Vérification de la santé des services"
    echo "  logs [SERVICE]  Affichage des logs (tous ou service spécifique)"
    echo "  monitor         Monitoring en temps réel"
    echo "  init            Initialisation des données uniquement"
    echo "  help            Affichage de cette aide"
    echo ""
    echo "Exemples:"
    echo "  $0 start                    # Démarrage complet"
    echo "  $0 logs event-bus-service   # Logs du service event-bus"
    echo "  $0 test                     # Tous les tests"
    echo "  $0 cleanup --full           # Nettoyage complet"
}

# Démarrage complet
start_complete() {
    log_info "Démarrage complet du Lab 7..."
    
    check_prerequisites
    cleanup
    start_infrastructure
    start_services
    
    if check_services_health; then
        init_data
        log_success "Lab 7 démarré avec succès!"
        log_info "Services disponibles:"
        echo "  - Event Bus Service: http://localhost:5000"
        echo "  - Inventory Service: http://localhost:5001"
        echo "  - Procurement Service: http://localhost:5002"
        echo "  - Supplier Service: http://localhost:5003"
        echo "  - Analytics Service: http://localhost:5007"
        echo "  - API Gateway: http://localhost:8080"
        echo "  - Web Interface: http://localhost:5008"
        echo "  - Grafana: http://localhost:3000 (admin/admin)"
        echo "  - Prometheus: http://localhost:9090"
        echo ""
        log_info "Utilisez '$0 test' pour exécuter les tests"
        log_info "Utilisez '$0 monitor' pour le monitoring en temps réel"
    else
        log_error "Échec du démarrage - vérifiez les logs"
        exit 1
    fi
}

# Main
main() {
    cd "$LAB7_DIR"
    
    case "${1:-help}" in
        "start")
            start_complete
            ;;
        "stop")
            cleanup
            ;;
        "restart")
            cleanup
            start_complete
            ;;
        "cleanup")
            cleanup "$2"
            ;;
        "test")
            run_tests
            ;;
        "health")
            check_services_health
            ;;
        "logs")
            show_logs "$2"
            ;;
        "monitor")
            monitor
            ;;
        "init")
            init_data
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Commande inconnue: $1"
            show_help
            exit 1
            ;;
    esac
}

# Exécution
main "$@"
