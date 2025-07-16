#!/usr/bin/env python3
"""
Script d'initialisation des données logistiques
Usage: python init_logistics_data.py
"""

import requests
import json
import time
from datetime import datetime, timedelta

# Configuration du service logistique
LOGISTICS_SERVICE_URL = 'http://localhost:5007'

def wait_for_service(url, service_name):
    """Attendre qu'un service soit disponible"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ {service_name} service is ready")
                return True
        except requests.exceptions.RequestException:
            pass
        print(f"⏳ Waiting for {service_name} service... (attempt {attempt + 1}/{max_attempts})")
        time.sleep(2)
    print(f"❌ {service_name} service failed to start")
    return False

def init_warehouse_inventory():
    """Initialiser l'inventaire du centre logistique"""
    print("\n📦 Initializing Warehouse Inventory...")
    
    # Récupérer les produits d'abord
    try:
        products_response = requests.get('http://localhost:5002/products')
        products = products_response.json() if products_response.status_code == 200 else []
    except:
        products = []
    
    if not products:
        print("⚠️ No products found, creating sample inventory")
        # Créer un inventaire de base avec des IDs fictifs
        inventory_data = [
            {"product_id": 1, "quantity_available": 100, "quantity_reserved": 0},
            {"product_id": 2, "quantity_available": 150, "quantity_reserved": 0},
            {"product_id": 3, "quantity_available": 80, "quantity_reserved": 0},
            {"product_id": 4, "quantity_available": 120, "quantity_reserved": 0},
            {"product_id": 5, "quantity_available": 90, "quantity_reserved": 0},
            {"product_id": 6, "quantity_available": 60, "quantity_reserved": 0},
            {"product_id": 7, "quantity_available": 200, "quantity_reserved": 0},
            {"product_id": 8, "quantity_available": 180, "quantity_reserved": 0},
            {"product_id": 9, "quantity_available": 25, "quantity_reserved": 0},
            {"product_id": 10, "quantity_available": 15, "quantity_reserved": 0},
            {"product_id": 11, "quantity_available": 12, "quantity_reserved": 0},
            {"product_id": 12, "quantity_available": 8, "quantity_reserved": 0},
            {"product_id": 13, "quantity_available": 6, "quantity_reserved": 0},
            {"product_id": 14, "quantity_available": 50, "quantity_reserved": 0},
            {"product_id": 15, "quantity_available": 30, "quantity_reserved": 0},
            {"product_id": 16, "quantity_available": 40, "quantity_reserved": 0},
            {"product_id": 17, "quantity_available": 35, "quantity_reserved": 0},
            {"product_id": 18, "quantity_available": 45, "quantity_reserved": 0},
            {"product_id": 19, "quantity_available": 20, "quantity_reserved": 0},
            {"product_id": 20, "quantity_available": 25, "quantity_reserved": 0},
            {"product_id": 21, "quantity_available": 15, "quantity_reserved": 0},
            {"product_id": 22, "quantity_available": 10, "quantity_reserved": 0},
            {"product_id": 23, "quantity_available": 8, "quantity_reserved": 0},
            {"product_id": 24, "quantity_available": 12, "quantity_reserved": 0},
            {"product_id": 25, "quantity_available": 18, "quantity_reserved": 0}
        ]
    else:
        # Utiliser les vrais produits
        inventory_data = []
        for i, product in enumerate(products[:25]):  # Limiter aux 25 premiers produits
            # Quantités variables selon le type de produit
            if 'alimentaire' in product.get('category', ''):
                quantity = 100 + (i * 10)  # Plus de stock pour l'alimentaire
            elif 'electromenager' in product.get('category', ''):
                quantity = 15 + (i * 2)  # Moins de stock pour l'électroménager
            elif 'vetements' in product.get('category', ''):
                quantity = 50 + (i * 5)  # Stock moyen pour les vêtements
            elif 'livres' in product.get('category', ''):
                quantity = 30 + (i * 3)  # Stock moyen pour les livres
            else:  # maison
                quantity = 25 + (i * 4)  # Stock moyen pour la maison
            
            inventory_data.append({
                "product_id": product['id'],
                "quantity_available": quantity,
                "quantity_reserved": 0
            })
    
    # Créer l'inventaire
    for item in inventory_data:
        try:
            response = requests.put(
                f"{LOGISTICS_SERVICE_URL}/warehouse-inventory/{item['product_id']}",
                json=item,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 200:
                print(f"✅ Created inventory for product {item['product_id']}: {item['quantity_available']} units")
            else:
                print(f"⚠️ Failed to create inventory for product {item['product_id']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating inventory for product {item['product_id']}: {e}")

def init_delivery_schedules():
    """Initialiser quelques plannings de livraison"""
    print("\n🚚 Initializing Delivery Schedules...")
    
    # Créer des plannings pour les prochains jours
    schedules = [
        {
            "store_id": 1,
            "scheduled_date": (datetime.now() + timedelta(days=1)).isoformat(),
            "driver_name": "Jean Tremblay",
            "vehicle_id": "CAM-001",
            "notes": "Livraison matinale - Produits frais prioritaires"
        },
        {
            "store_id": 2,
            "scheduled_date": (datetime.now() + timedelta(days=2)).isoformat(),
            "driver_name": "Marie Dubois",
            "vehicle_id": "CAM-002",
            "notes": "Livraison complète - Tous produits"
        },
        {
            "store_id": 3,
            "scheduled_date": (datetime.now() + timedelta(days=1, hours=6)).isoformat(),
            "driver_name": "Pierre Lavoie",
            "vehicle_id": "CAM-003",
            "notes": "Livraison express - Stock urgent"
        },
        {
            "store_id": 4,
            "scheduled_date": (datetime.now() + timedelta(days=3)).isoformat(),
            "driver_name": "Sophie Martin",
            "vehicle_id": "CAM-004",
            "notes": "Livraison régulière - Réapprovisionnement hebdomadaire"
        }
    ]
    
    for schedule in schedules:
        try:
            response = requests.post(
                f"{LOGISTICS_SERVICE_URL}/delivery-schedules",
                json=schedule,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 201:
                print(f"✅ Created delivery schedule for store {schedule['store_id']}")
            else:
                print(f"⚠️ Failed to create delivery schedule: {response.text}")
        except Exception as e:
            print(f"❌ Error creating delivery schedule: {e}")

def main():
    """Fonction principale"""
    print("🚀 Starting logistics data initialization...")
    
    # Attendre que le service logistique soit prêt
    if not wait_for_service(LOGISTICS_SERVICE_URL, 'Logistics'):
        print("❌ Logistics service is not ready. Please check your docker-compose setup.")
        return
    
    print("\n✅ Logistics service is ready! Starting data initialization...")
    
    # Initialiser les données
    init_warehouse_inventory()
    init_delivery_schedules()
    
    print("\n🎉 Logistics data initialization completed!")
    print("\n📋 Summary of created data:")
    print("- Inventaire du centre logistique pour 25 produits")
    print("- 4 plannings de livraison pour les prochains jours")
    print("\n🔧 Next steps:")
    print("1. Connectez-vous en tant que responsable logistique")
    print("2. Consultez les demandes de réapprovisionnement")
    print("3. Gérez l'inventaire du centre logistique")
    print("4. Planifiez les livraisons")

if __name__ == "__main__":
    main() 