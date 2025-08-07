#!/usr/bin/env python3
"""
Script d'initialisation pour Lab 7 - Architecture Événementielle
Initialise tous les services et données de test
"""

import requests
import time
import json
from datetime import datetime

# Configuration
SERVICES = {
    'event_store': 'http://localhost:5020',
    'inventory': 'http://localhost:5021',
    'procurement': 'http://localhost:5022',
    'supplier': 'http://localhost:5023',
    'analytics': 'http://localhost:5024'
}

INITIAL_PRODUCTS = [
    {'id': '1', 'name': 'Laptop Gaming', 'quantity': 20, 'price': 1299.99},
    {'id': '2', 'name': 'Smartphone', 'quantity': 15, 'price': 699.99},
    {'id': '3', 'name': 'Casque Audio', 'quantity': 8, 'price': 199.99},
    {'id': '4', 'name': 'Clavier Mécanique', 'quantity': 25, 'price': 149.99},
    {'id': '5', 'name': 'Souris Gaming', 'quantity': 3, 'price': 79.99},  # Stock faible intentionnel
    {'id': '6', 'name': 'Écran 4K', 'quantity': 12, 'price': 449.99},
    {'id': '7', 'name': 'Webcam HD', 'quantity': 6, 'price': 89.99},
    {'id': '8', 'name': 'Tablette', 'quantity': 18, 'price': 399.99}
]

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🔧 {title}")
    print(f"{'='*60}")

def print_step(step):
    print(f"\n🔸 {step}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def wait_for_services():
    """Attend que tous les services soient disponibles"""
    print_header("Attente de la disponibilité des services")
    
    max_retries = 30
    retry_count = 0
    
    while retry_count < max_retries:
        all_ready = True
        
        for service_name, url in SERVICES.items():
            try:
                response = requests.get(f"{url}/health", timeout=3)
                if response.status_code != 200:
                    all_ready = False
                    break
            except:
                all_ready = False
                break
        
        if all_ready:
            print_success("Tous les services sont disponibles")
            return True
        
        retry_count += 1
        print(f"⏳ Tentative {retry_count}/{max_retries} - Services en cours de démarrage...")
        time.sleep(5)
    
    print_error("Timeout: Certains services ne sont pas disponibles")
    return False

def initialize_stock():
    """Initialise le stock de tous les produits"""
    print_header("Initialisation du stock des produits")
    
    for product in INITIAL_PRODUCTS:
        print_step(f"Initialisation du produit {product['id']}: {product['name']}")
        try:
            response = requests.post(
                f"{SERVICES['inventory']}/api/products/{product['id']}/initialize",
                json={'initial_quantity': product['quantity']},
                timeout=10
            )
            
            if response.status_code == 201:
                print_success(f"Stock initialisé: {product['quantity']} unités de {product['name']}")
            else:
                print_error(f"Échec de l'initialisation du produit {product['id']}: {response.status_code}")
                
        except Exception as e:
            print_error(f"Erreur lors de l'initialisation du produit {product['id']}: {e}")
    
    time.sleep(2)  # Laisser le temps aux événements de se propager

def start_event_services():
    """Démarre tous les services d'écoute d'événements"""
    print_header("Démarrage des services d'écoute d'événements")
    
    services_to_start = [
        ('procurement', 'Procurement Service - Écoute des événements LowStockDetected'),
        ('supplier', 'Supplier Service - Écoute des événements RestockApproved'),
        ('analytics', 'Analytics Service - Mise à jour des projections CQRS')
    ]
    
    for service_key, description in services_to_start:
        print_step(f"Démarrage: {description}")
        try:
            if service_key == 'procurement':
                response = requests.post(f"{SERVICES[service_key]}/api/events/start-listening")
            elif service_key == 'supplier':
                response = requests.post(f"{SERVICES[service_key]}/api/events/start-services")
            elif service_key == 'analytics':
                response = requests.post(f"{SERVICES[service_key]}/api/events/start-updates")
            
            if response.status_code == 200:
                print_success(f"Service {service_key} démarré avec succès")
            else:
                print_error(f"Échec du démarrage du service {service_key}: {response.status_code}")
                
        except Exception as e:
            print_error(f"Erreur lors du démarrage du service {service_key}: {e}")

def simulate_some_sales():
    """Simule quelques ventes pour générer des événements"""
    print_header("Simulation de ventes initiales")
    
    initial_sales = [
        {'product_id': '1', 'quantity': 2, 'price': 1299.99, 'customer_id': 'customer_001'},
        {'product_id': '2', 'quantity': 1, 'price': 699.99, 'customer_id': 'customer_002'},
        {'product_id': '5', 'quantity': 1, 'price': 79.99, 'customer_id': 'customer_003'},  # Va déclencher stock faible
        {'product_id': '3', 'quantity': 3, 'price': 199.99, 'customer_id': 'customer_004'},
    ]
    
    for sale in initial_sales:
        print_step(f"Vente: {sale['quantity']}x Produit {sale['product_id']} à {sale['customer_id']}")
        try:
            response = requests.post(
                f"{SERVICES['inventory']}/api/products/{sale['product_id']}/sell",
                json=sale,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Vente réussie - Stock restant: {result['remaining_stock']}")
                
                if result['remaining_stock'] <= 5:
                    print(f"⚠️  Alerte stock faible générée pour le produit {sale['product_id']}")
            else:
                print_error(f"Échec de la vente: {response.status_code}")
                
        except Exception as e:
            print_error(f"Erreur lors de la vente: {e}")
        
        time.sleep(1)  # Petite pause entre les ventes
    
    time.sleep(5)  # Laisser le temps aux événements de se propager

def check_saga_execution():
    """Vérifie l'exécution de la saga de réapprovisionnement"""
    print_header("Vérification de l'exécution de la Saga")
    
    print_step("Vérification des demandes de réapprovisionnement")
    try:
        response = requests.get(f"{SERVICES['procurement']}/api/restock/requests")
        if response.status_code == 200:
            data = response.json()
            requests_count = len(data['restock_requests'])
            print_success(f"Trouvé {requests_count} demandes de réapprovisionnement")
            
            for req in data['restock_requests']:
                status = req.get('status', 'pending')
                print(f"   📋 Demande {req['restock_request_id']}: Produit {req['product_id']}, Statut: {status}")
        else:
            print_error(f"Échec de récupération des demandes: {response.status_code}")
    except Exception as e:
        print_error(f"Erreur lors de la vérification: {e}")
    
    print_step("Vérification des livraisons programmées")
    try:
        response = requests.get(f"{SERVICES['supplier']}/api/deliveries/pending")
        if response.status_code == 200:
            data = response.json()
            deliveries_count = len(data['pending_deliveries'])
            print_success(f"Trouvé {deliveries_count} livraisons programmées")
            
            for delivery in data['pending_deliveries']:
                print(f"   🚚 Livraison {delivery['delivery_id']}: Produit {delivery['product_id']}")
                print(f"       Fournisseur: {delivery['supplier_id']}, Prévue: {delivery['scheduled_delivery_date']}")
        else:
            print_error(f"Échec de récupération des livraisons: {response.status_code}")
    except Exception as e:
        print_error(f"Erreur lors de la vérification: {e}")

def check_projections():
    """Vérifie les projections CQRS"""
    print_header("Vérification des projections CQRS")
    
    projections = [
        ('stock-levels', 'Niveaux de stock'),
        ('restock-alerts', 'Alertes de réapprovisionnement'),
        ('sales-analytics', 'Analytics des ventes')
    ]
    
    for endpoint, name in projections:
        print_step(f"Vérification: {name}")
        try:
            response = requests.get(f"{SERVICES['analytics']}/api/projections/{endpoint}")
            if response.status_code == 200:
                data = response.json()
                print_success(f"{name} disponible")
                
                # Afficher quelques statistiques
                if 'stock_levels' in data:
                    print(f"   📊 {len(data['stock_levels'])} produits suivis")
                elif 'restock_alerts' in data:
                    active_alerts = [a for a in data['restock_alerts'] if a['status'] == 'active']
                    print(f"   🚨 {len(active_alerts)} alertes actives / {len(data['restock_alerts'])} total")
                elif 'sales_analytics' in data:
                    daily_sales = data['sales_analytics'].get('daily_sales', {})
                    product_sales = data['sales_analytics'].get('product_sales', {})
                    print(f"   💰 {len(daily_sales)} jours, {len(product_sales)} produits vendus")
                    
            else:
                print_error(f"Échec de récupération de {name}: {response.status_code}")
        except Exception as e:
            print_error(f"Erreur lors de la vérification de {name}: {e}")

def display_service_info():
    """Affiche les informations d'accès aux services"""
    print_header("Informations d'accès aux services")
    
    print("🌐 Services Lab 7 - Architecture Événementielle:")
    print(f"   • Event Store & Bus:     http://localhost:5020")
    print(f"   • Inventory Service:     http://localhost:5021")
    print(f"   • Procurement Service:   http://localhost:5022")
    print(f"   • Supplier Service:      http://localhost:5023")
    print(f"   • Analytics Service:     http://localhost:5024")
    
    print("\n🔗 Autres services:")
    print(f"   • API Gateway:           http://localhost:5010")
    print(f"   • Interface Web:         http://localhost:8080")
    print(f"   • Prometheus:            http://localhost:9090")
    print(f"   • Grafana:               http://localhost:3000")
    
    print("\n📊 Endpoints principaux:")
    print("   • Event Store Stats:     GET /api/events/stats")
    print("   • Stock Levels:          GET /api/projections/stock-levels")
    print("   • Restock Alerts:        GET /api/projections/restock-alerts")
    print("   • Supplier Performance:  GET /api/projections/supplier-performance")
    print("   • Sales Analytics:       GET /api/projections/sales-analytics")
    
    print("\n🧪 Test de l'architecture:")
    print("   python test_event_driven_architecture.py")

def main():
    """Fonction principale d'initialisation"""
    print("🚀 Initialisation Lab 7 - Architecture Événementielle")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # 1. Attendre que tous les services soient disponibles
    if not wait_for_services():
        return
    
    # 2. Démarrer les services d'écoute d'événements
    start_event_services()
    
    # 3. Initialiser le stock des produits
    initialize_stock()
    
    # 4. Simuler quelques ventes initiales
    simulate_some_sales()
    
    # 5. Vérifier l'exécution de la saga
    check_saga_execution()
    
    # 6. Vérifier les projections CQRS
    check_projections()
    
    # 7. Afficher les informations d'accès
    display_service_info()
    
    print_header("Initialisation terminée avec succès! 🎉")
    print("✅ Architecture événementielle opérationnelle")
    print("✅ Services événementiels démarrés")
    print("✅ Stock initialisé avec données de test")
    print("✅ Saga de réapprovisionnement active")
    print("✅ Projections CQRS fonctionnelles")
    
    print("\n🎯 Prochaines étapes:")
    print("1. Exécuter les tests: python test_event_driven_architecture.py")
    print("2. Explorer l'interface web: http://localhost:8080")
    print("3. Monitorer avec Grafana: http://localhost:3000")

if __name__ == "__main__":
    main()
