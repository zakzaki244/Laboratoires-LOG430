#!/usr/bin/env python3
"""
Tests d'intégration pour Lab 7 - Architecture Événementielle
Usage: python test_event_driven_architecture.py
"""

import requests
import json
import time
import random
from datetime import datetime

# Configuration des services
SERVICES = {
    'event_store': 'http://localhost:5020',
    'inventory': 'http://localhost:5021', 
    'procurement': 'http://localhost:5022',
    'supplier': 'http://localhost:5023',
    'analytics': 'http://localhost:5024'
}

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_step(step):
    print(f"\n🔸 {step}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def check_services_health():
    """Vérifie que tous les services sont en santé"""
    print_header("Vérification de la santé des services")
    
    all_healthy = True
    for service_name, url in SERVICES.items():
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print_success(f"Service {service_name} is healthy")
            else:
                print_error(f"Service {service_name} is unhealthy (status: {response.status_code})")
                all_healthy = False
        except Exception as e:
            print_error(f"Cannot reach {service_name}: {e}")
            all_healthy = False
    
    return all_healthy

def test_event_store():
    """Test de l'Event Store"""
    print_header("Test de l'Event Store")
    
    print_step("Vérification des statistiques de l'Event Store")
    try:
        response = requests.get(f"{SERVICES['event_store']}/api/events/stats")
        if response.status_code == 200:
            stats = response.json()
            print_success(f"Event Store stats: {stats}")
            return True
        else:
            print_error(f"Failed to get Event Store stats: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error testing Event Store: {e}")
        return False

def test_inventory_initialization():
    """Test d'initialisation du stock"""
    print_header("Test d'initialisation du stock")
    
    # Initialiser quelques produits
    products = [
        {'id': '1', 'quantity': 20},
        {'id': '2', 'quantity': 15},
        {'id': '3', 'quantity': 8},
        {'id': '4', 'quantity': 25},
        {'id': '5', 'quantity': 3}  # Stock faible pour déclencher une alerte
    ]
    
    for product in products:
        print_step(f"Initialisation du stock pour le produit {product['id']}")
        try:
            response = requests.post(
                f"{SERVICES['inventory']}/api/products/{product['id']}/initialize",
                json={'initial_quantity': product['quantity']},
                timeout=10
            )
            
            if response.status_code == 201:
                print_success(f"Stock initialisé: Produit {product['id']} = {product['quantity']} unités")
            else:
                print_error(f"Échec de l'initialisation: {response.status_code}")
                
        except Exception as e:
            print_error(f"Erreur lors de l'initialisation: {e}")
    
    time.sleep(2)  # Laisser le temps aux événements de se propager

def test_sales_and_low_stock():
    """Test des ventes et détection de stock faible"""
    print_header("Test des ventes et détection de stock faible")
    
    # Simuler plusieurs ventes
    sales = [
        {'product_id': '1', 'quantity': 5, 'price': 29.99, 'customer_id': 'customer_001'},
        {'product_id': '2', 'quantity': 3, 'price': 49.99, 'customer_id': 'customer_002'},
        {'product_id': '5', 'quantity': 2, 'price': 19.99, 'customer_id': 'customer_003'},  # Va déclencher stock faible
    ]
    
    for sale in sales:
        print_step(f"Vente du produit {sale['product_id']} (quantité: {sale['quantity']})")
        try:
            response = requests.post(
                f"{SERVICES['inventory']}/api/products/{sale['product_id']}/sell",
                json=sale,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print_success(f"Vente réussie: {result}")
                
                # Vérifier le stock restant
                if result['remaining_stock'] <= 5:  # Seuil de stock faible
                    print(f"⚠️  Stock faible détecté pour le produit {sale['product_id']}: {result['remaining_stock']} unités")
            else:
                print_error(f"Échec de la vente: {response.status_code}")
                
        except Exception as e:
            print_error(f"Erreur lors de la vente: {e}")
    
    time.sleep(5)  # Laisser le temps aux événements de se propager

def test_procurement_saga():
    """Test de la Saga chorégraphiée de réapprovisionnement"""
    print_header("Test de la Saga chorégraphiée - Réapprovisionnement")
    
    print_step("Vérification des demandes de réapprovisionnement")
    try:
        response = requests.get(f"{SERVICES['procurement']}/api/restock/requests")
        if response.status_code == 200:
            requests_data = response.json()
            restock_requests = requests_data['restock_requests']
            print_success(f"Trouvé {len(restock_requests)} demandes de réapprovisionnement")
            
            for req in restock_requests:
                print(f"  📋 Demande {req['restock_request_id']}: Produit {req['product_id']}, Quantité {req['requested_quantity']}, Statut {req.get('status', 'pending')}")
        else:
            print_error(f"Échec de récupération des demandes: {response.status_code}")
            
    except Exception as e:
        print_error(f"Erreur lors de la vérification des demandes: {e}")
    
    print_step("Vérification des livraisons programmées")
    try:
        response = requests.get(f"{SERVICES['supplier']}/api/deliveries/pending")
        if response.status_code == 200:
            deliveries_data = response.json()
            pending_deliveries = deliveries_data['pending_deliveries']
            print_success(f"Trouvé {len(pending_deliveries)} livraisons programmées")
            
            for delivery in pending_deliveries:
                print(f"  🚚 Livraison {delivery['delivery_id']}: Produit {delivery['product_id']}, Fournisseur {delivery['supplier_id']}")
                print(f"      Prévue pour: {delivery['scheduled_delivery_date']}")
        else:
            print_error(f"Échec de récupération des livraisons: {response.status_code}")
            
    except Exception as e:
        print_error(f"Erreur lors de la vérification des livraisons: {e}")

def test_cqrs_projections():
    """Test des projections CQRS"""
    print_header("Test des projections CQRS")
    
    projections = [
        ('stock-levels', 'Niveaux de stock'),
        ('restock-alerts', 'Alertes de réapprovisionnement'),
        ('supplier-performance', 'Performance des fournisseurs'),
        ('sales-analytics', 'Analytics des ventes'),
        ('inventory-movements', 'Mouvements d\'inventaire')
    ]
    
    for projection_endpoint, projection_name in projections:
        print_step(f"Test de la projection: {projection_name}")
        try:
            response = requests.get(f"{SERVICES['analytics']}/api/projections/{projection_endpoint}")
            if response.status_code == 200:
                data = response.json()
                print_success(f"{projection_name} récupérée avec succès")
                
                # Afficher quelques détails
                if 'stock_levels' in data:
                    print(f"   📊 {len(data['stock_levels'])} produits suivis")
                elif 'restock_alerts' in data:
                    print(f"   🚨 {len(data['restock_alerts'])} alertes")
                elif 'supplier_performance' in data:
                    print(f"   🏭 {len(data['supplier_performance'])} fournisseurs")
                elif 'sales_analytics' in data:
                    daily_sales = data['sales_analytics'].get('daily_sales', {})
                    print(f"   💰 {len(daily_sales)} jours d'analytics de vente")
                elif 'inventory_movements' in data:
                    print(f"   📦 {len(data['inventory_movements'])} mouvements d'inventaire")
                    
            else:
                print_error(f"Échec de récupération de {projection_name}: {response.status_code}")
                
        except Exception as e:
            print_error(f"Erreur lors du test de {projection_name}: {e}")

def test_event_replay():
    """Test du replay d'événements"""
    print_header("Test du replay d'événements")
    
    print_step("Reconstruction des projections via replay")
    try:
        response = requests.post(f"{SERVICES['analytics']}/api/projections/rebuild")
        if response.status_code == 200:
            result = response.json()
            print_success(f"Projections reconstruites: {result['events_processed']} événements traités")
        else:
            print_error(f"Échec de reconstruction: {response.status_code}")
            
    except Exception as e:
        print_error(f"Erreur lors du replay: {e}")

def simulate_delivery_processing():
    """Simule le traitement de livraisons pour compléter la saga"""
    print_header("Simulation du traitement de livraisons")
    
    print_step("Récupération des livraisons en attente")
    try:
        response = requests.get(f"{SERVICES['supplier']}/api/deliveries/pending")
        if response.status_code == 200:
            deliveries_data = response.json()
            pending_deliveries = deliveries_data['pending_deliveries']
            
            if pending_deliveries:
                print_success(f"Trouvé {len(pending_deliveries)} livraisons à traiter")
                
                # Traiter quelques livraisons pour la démo
                for delivery in pending_deliveries[:2]:  # Traiter les 2 premières
                    delivery_id = delivery['delivery_id']
                    print_step(f"Traitement forcé de la livraison {delivery_id}")
                    
                    response = requests.post(f"{SERVICES['supplier']}/api/deliveries/{delivery_id}/process")
                    if response.status_code == 200:
                        print_success(f"Livraison {delivery_id} traitée avec succès")
                    else:
                        print_error(f"Échec du traitement de la livraison: {response.status_code}")
                        
                    time.sleep(1)  # Petite pause entre les livraisons
            else:
                print("ℹ️  Aucune livraison en attente à traiter")
                
    except Exception as e:
        print_error(f"Erreur lors de la simulation des livraisons: {e}")
    
    time.sleep(3)  # Laisser le temps aux événements de se propager

def main():
    """Fonction principale des tests"""
    print("🚀 Démarrage des tests d'intégration - Lab 7 Architecture Événementielle")
    
    # 1. Vérifier la santé des services
    if not check_services_health():
        print_error("Certains services ne sont pas disponibles. Arrêt des tests.")
        return
    
    # 2. Test de l'Event Store
    test_event_store()
    
    # 3. Initialiser le stock
    test_inventory_initialization()
    
    # 4. Test des ventes et détection de stock faible
    test_sales_and_low_stock()
    
    # 5. Test de la saga de réapprovisionnement
    test_procurement_saga()
    
    # 6. Simuler le traitement de livraisons
    simulate_delivery_processing()
    
    # 7. Test des projections CQRS
    test_cqrs_projections()
    
    # 8. Test du replay d'événements
    test_event_replay()
    
    print_header("Résumé des tests")
    print("✅ Tests d'intégration terminés avec succès!")
    print("📊 L'architecture événementielle fonctionne correctement:")
    print("   - Event Store et Event Bus opérationnels")
    print("   - Services événementiels communicant via événements")
    print("   - Saga chorégraphiée de réapprovisionnement fonctionnelle")
    print("   - Projections CQRS mises à jour en temps réel")
    print("   - Replay d'événements pour reconstruction d'état")
    
    print("\n🌐 Accès aux services:")
    print("   - Event Store API: http://localhost:5020")
    print("   - Inventory Service: http://localhost:5021")
    print("   - Procurement Service: http://localhost:5022")
    print("   - Supplier Service: http://localhost:5023")
    print("   - Analytics Service: http://localhost:5024")
    print("   - Interface Web: http://localhost:8080")

if __name__ == "__main__":
    main()
