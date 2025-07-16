#!/usr/bin/env python3
"""
Script d'initialisation des données de base pour tous les microservices
Usage: python init_all_data.py
"""

import requests
import json
import time
from datetime import datetime

# Configuration des services
SERVICES = {
    'customer': 'http://10.194.32.174:5001',
    'product': 'http://10.194.32.174:5002',
    'sales': 'http://10.194.32.174:5003',
    'store': 'http://10.194.32.174:5004',
    'cart': 'http://10.194.32.174:5005',
    'checkout': 'http://10.194.32.174:5006',
    'logistics': 'http://10.194.32.174:5007'
}

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

def init_customer_service():
    """Initialiser les données utilisateurs"""
    print("\n🔧 Initializing Customer Service...")
    
    customers = [
        {
            "name": "Admin Principal",
            "email": "admin@supermarche.com",
            "password": "admin123",
            "role": "admin",
            "phone": "514-555-0001",
            "address": "123 Rue Admin, Montréal, QC"
        },
        {
            "name": "Manager Général",
            "email": "manager@supermarche.com",
            "password": "manager123",
            "role": "manager",
            "phone": "514-555-0002",
            "address": "456 Rue Manager, Montréal, QC"
        },
        {
            "name": "Gestionnaire Produits",
            "email": "product@supermarche.com",
            "password": "product123",
            "role": "product_manage",
            "phone": "514-555-0003",
            "address": "789 Rue Product, Montréal, QC"
        },
        {
            "name": "Responsable Logistique",
            "email": "logistics@supermarche.com",
            "password": "logistics123",
            "role": "logistics",
            "phone": "514-555-0004",
            "address": "321 Rue Logistics, Montréal, QC"
        },
        {
            "name": "Jean Dupont",
            "email": "client1@example.com",
            "password": "client123",
            "role": "client",
            "phone": "514-555-1001",
            "address": "100 Rue Client, Montréal, QC"
        },
        {
            "name": "Marie Martin",
            "email": "client2@example.com",
            "password": "client123",
            "role": "client",
            "phone": "514-555-1002",
            "address": "200 Rue Client, Montréal, QC"
        },
        {
            "name": "Pierre Durand",
            "email": "client3@example.com",
            "password": "client123",
            "role": "client",
            "phone": "514-555-1003",
            "address": "300 Rue Client, Montréal, QC"
        }
    ]
    
    for customer in customers:
        try:
            response = requests.post(
                f"{SERVICES['customer']}/customers",
                json=customer,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 201:
                print(f"✅ Created customer: {customer['name']}")
            else:
                print(f"⚠️ Failed to create customer {customer['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating customer {customer['name']}: {e}")

def init_store_service():
    """Initialiser les magasins et le centre logistique"""
    print("\n🏪 Initializing Store Service...")
    
    stores = [
        {
            "name": "SuperMarché Centre-Ville",
            "address": "1000 Rue Sainte-Catherine, Montréal, QC",
            "phone": "514-555-2001",
            "email": "centreville@supermarche.com",
            "type": "retail"
        },
        {
            "name": "SuperMarché Westmount",
            "address": "2000 Avenue Greene, Westmount, QC",
            "phone": "514-555-2002",
            "email": "westmount@supermarche.com",
            "type": "retail"
        },
        {
            "name": "SuperMarché Laval",
            "address": "3000 Boulevard des Laurentides, Laval, QC",
            "phone": "514-555-2003",
            "email": "laval@supermarche.com",
            "type": "retail"
        },
        {
            "name": "SuperMarché Brossard",
            "address": "4000 Boulevard Taschereau, Brossard, QC",
            "phone": "514-555-2004",
            "email": "brossard@supermarche.com",
            "type": "retail"
        },
        {
            "name": "Centre Logistique Principal",
            "address": "5000 Boulevard Industriel, Montréal, QC",
            "phone": "514-555-2005",
            "email": "logistics@supermarche.com",
            "type": "warehouse"
        }
    ]
    
    for store in stores:
        try:
            response = requests.post(
                f"{SERVICES['store']}/stores",
                json=store,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 201:
                print(f"✅ Created store: {store['name']} ({store['type']})")
            else:
                print(f"⚠️ Failed to create store {store['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating store {store['name']}: {e}")

def init_product_service():
    """Initialiser les produits par catégories"""
    print("\n📦 Initializing Product Service...")
    
    # Récupérer les magasins d'abord
    try:
        stores_response = requests.get(f"{SERVICES['store']}/stores")
        stores = stores_response.json() if stores_response.status_code == 200 else []
    except:
        stores = []
    
    if not stores:
        print("⚠️ No stores found, creating products without store association")
        store_ids = [None]
    else:
        store_ids = [store['id'] for store in stores]
    
    products = [
        # ===== ALIMENTAIRE =====
        # Fruits et Légumes
        {
            "name": "Pommes Gala (1kg)",
            "description": "Pommes fraîches et juteuses, parfaites pour la collation",
            "price": 4.99,
            "stock": 50,
            "min_stock": 15,
            "category": "alimentaire_fruits_legumes",
            "store_id": store_ids[0] if store_ids else None,
            "expiry_date": "2024-02-15"
        },
        {
            "name": "Bananes (1kg)",
            "description": "Bananes biologiques, riches en potassium",
            "price": 3.49,
            "stock": 75,
            "min_stock": 20,
            "category": "alimentaire_fruits_legumes",
            "store_id": store_ids[0] if store_ids else None,
            "expiry_date": "2024-02-10"
        },
        {
            "name": "Tomates (500g)",
            "description": "Tomates cerises fraîches du Québec",
            "price": 5.99,
            "stock": 30,
            "min_stock": 10,
            "category": "alimentaire_fruits_legumes",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0],
            "expiry_date": "2024-02-08"
        },
        
        # Produits Laitiers
        {
            "name": "Lait 2% (2L)",
            "description": "Lait frais du Québec, 2% de matières grasses",
            "price": 4.49,
            "stock": 40,
            "min_stock": 12,
            "category": "alimentaire_laitiers",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0],
            "expiry_date": "2024-02-12"
        },
        {
            "name": "Fromage Cheddar (500g)",
            "description": "Fromage cheddar vieilli, riche en saveur",
            "price": 8.99,
            "stock": 20,
            "min_stock": 6,
            "category": "alimentaire_laitiers",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0],
            "expiry_date": "2024-03-01"
        },
        
        # Viandes et Poissons
        {
            "name": "Poulet Entier (2kg)",
            "description": "Poulet frais du Québec, élevé sans antibiotiques",
            "price": 15.99,
            "stock": 15,
            "min_stock": 5,
            "category": "alimentaire_viandes",
            "store_id": store_ids[0] if store_ids else None,
            "expiry_date": "2024-02-07"
        },
        {
            "name": "Saumon Atlantique (500g)",
            "description": "Filet de saumon frais, riche en oméga-3",
            "price": 24.99,
            "stock": 10,
            "min_stock": 3,
            "category": "alimentaire_viandes",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0],
            "expiry_date": "2024-02-06"
        },
        
        # Produits Secs
        {
            "name": "Riz Basmati (2kg)",
            "description": "Riz basmati parfumé, grain long",
            "price": 7.99,
            "stock": 60,
            "min_stock": 15,
            "category": "alimentaire_secs",
            "store_id": store_ids[3] if len(store_ids) > 3 else store_ids[0],
            "expiry_date": "2025-01-01"
        },
        {
            "name": "Pâtes Spaghetti (500g)",
            "description": "Pâtes de blé dur, cuisson al dente",
            "price": 2.49,
            "stock": 80,
            "min_stock": 20,
            "category": "alimentaire_secs",
            "store_id": store_ids[0] if store_ids else None,
            "expiry_date": "2025-06-01"
        },
        
        # ===== ÉLECTROMÉNAGER =====
        {
            "name": "Mixeur KitchenAid",
            "description": "Mixeur professionnel 5 vitesses, 350W",
            "price": 89.99,
            "stock": 12,
            "min_stock": 4,
            "category": "electromenager_cuisine",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Grille-pain Delonghi",
            "description": "Grille-pain 4 fentes, réglage de température",
            "price": 45.99,
            "stock": 18,
            "min_stock": 6,
            "category": "electromenager_cuisine",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Cafetière Nespresso",
            "description": "Machine à café automatique, 19 bars",
            "price": 199.99,
            "stock": 8,
            "min_stock": 3,
            "category": "electromenager_cuisine",
            "store_id": store_ids[3] if len(store_ids) > 3 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Aspirateur Dyson",
            "description": "Aspirateur sans fil, 60 minutes d'autonomie",
            "price": 399.99,
            "stock": 6,
            "min_stock": 2,
            "category": "electromenager_menage",
            "store_id": store_ids[0] if store_ids else None,
            "expiry_date": None
        },
        
        # ===== VÊTEMENTS =====
        {
            "name": "T-shirt Cotton (M)",
            "description": "T-shirt 100% coton bio, taille M",
            "price": 24.99,
            "stock": 35,
            "min_stock": 10,
            "category": "vetements_hauts",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Jean Levi's (32/32)",
            "description": "Jean classique, coupe slim, taille 32/32",
            "price": 79.99,
            "stock": 20,
            "min_stock": 6,
            "category": "vetements_bas",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Pull Hiver (L)",
            "description": "Pull en laine mérinos, taille L",
            "price": 89.99,
            "stock": 15,
            "min_stock": 5,
            "category": "vetements_hauts",
            "store_id": store_ids[3] if len(store_ids) > 3 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Chaussures Nike Air",
            "description": "Sneakers confortables, taille 42",
            "price": 129.99,
            "stock": 12,
            "min_stock": 4,
            "category": "vetements_chaussures",
            "store_id": store_ids[0] if store_ids else None,
            "expiry_date": None
        },
        
        # ===== LIVRES =====
        {
            "name": "Harry Potter Tome 1",
            "description": "Harry Potter à l'école des sorciers, édition collector",
            "price": 29.99,
            "stock": 25,
            "min_stock": 8,
            "category": "livres_roman",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Cuisine du Québec",
            "description": "Livre de recettes traditionnelles québécoises",
            "price": 34.99,
            "stock": 18,
            "min_stock": 6,
            "category": "livres_cuisine",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Guide Montréal 2024",
            "description": "Guide touristique complet de Montréal",
            "price": 19.99,
            "stock": 30,
            "min_stock": 10,
            "category": "livres_guide",
            "store_id": store_ids[3] if len(store_ids) > 3 else store_ids[0],
            "expiry_date": None
        },
        
        # ===== MAISON =====
        {
            "name": "Casserole Le Creuset",
            "description": "Casserole en fonte émaillée, 5L, rouge",
            "price": 249.99,
            "stock": 8,
            "min_stock": 3,
            "category": "maison_cuisine",
            "store_id": store_ids[0] if store_ids else None,
            "expiry_date": None
        },
        {
            "name": "Serviettes de Bain (6)",
            "description": "Serviettes 100% coton, 400g/m², 6 pièces",
            "price": 49.99,
            "stock": 22,
            "min_stock": 7,
            "category": "maison_salle_bain",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Lampadaire Design",
            "description": "Lampadaire moderne, hauteur 180cm, LED intégrée",
            "price": 179.99,
            "stock": 10,
            "min_stock": 4,
            "category": "maison_eclairage",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0],
            "expiry_date": None
        },
        {
            "name": "Coussin Décoratif (40x40)",
            "description": "Coussin en velours, 40x40cm, couleur bleu",
            "price": 34.99,
            "stock": 28,
            "min_stock": 9,
            "category": "maison_deco",
            "store_id": store_ids[3] if len(store_ids) > 3 else store_ids[0],
            "expiry_date": None
        }
    ]
    
    for product in products:
        try:
            response = requests.post(
                f"{SERVICES['product']}/products",
                json=product,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 201:
                print(f"✅ Created product: {product['name']} ({product['category']})")
            else:
                print(f"⚠️ Failed to create product {product['name']}: {response.text}")
        except Exception as e:
            print(f"❌ Error creating product {product['name']}: {e}")

def init_sales_service():
    """Initialiser quelques ventes de test"""
    print("\n💰 Initializing Sales Service...")
    
    # Récupérer les clients et produits
    try:
        customers_response = requests.get(f"{SERVICES['customer']}/customers")
        products_response = requests.get(f"{SERVICES['product']}/products")
        
        customers = customers_response.json() if customers_response.status_code == 200 else []
        products = products_response.json() if products_response.status_code == 200 else []
        
        if not customers or not products:
            print("⚠️ No customers or products found, skipping sales initialization")
            return
            
        # Créer quelques ventes de test
        sales = [
            {
                "customer_id": customers[4]['id'],  # Premier client
                "store_id": 1,
                "items": [
                    {"product_id": products[0]['id'], "quantity": 2, "unit_price": products[0]['price']},
                    {"product_id": products[4]['id'], "quantity": 1, "unit_price": products[4]['price']}
                ],
                "total_amount": (products[0]['price'] * 2) + products[4]['price']
            },
            {
                "customer_id": customers[5]['id'],  # Deuxième client
                "store_id": 2,
                "items": [
                    {"product_id": products[7]['id'], "quantity": 1, "unit_price": products[7]['price']},
                    {"product_id": products[10]['id'], "quantity": 3, "unit_price": products[10]['price']}
                ],
                "total_amount": products[7]['price'] + (products[10]['price'] * 3)
            }
        ]
        
        for sale in sales:
            try:
                response = requests.post(
                    f"{SERVICES['sales']}/sales",
                    json=sale,
                    headers={'Content-Type': 'application/json'}
                )
                if response.status_code == 201:
                    print(f"✅ Created sale for customer {sale['customer_id']}")
                else:
                    print(f"⚠️ Failed to create sale: {response.text}")
            except Exception as e:
                print(f"❌ Error creating sale: {e}")
                
    except Exception as e:
        print(f"❌ Error initializing sales: {e}")

def init_logistics_service():
    """Initialiser les données logistiques"""
    print("\n🚚 Initializing Logistics Service...")
    
    # Créer quelques demandes de réapprovisionnement
    restock_requests = [
        {
            "store_id": 1,
            "product_id": 1,
            "quantity_requested": 20,
            "priority": "high",
            "status": "pending"
        },
        {
            "store_id": 2,
            "product_id": 5,
            "quantity_requested": 15,
            "priority": "medium",
            "status": "approved"
        },
        {
            "store_id": 3,
            "product_id": 8,
            "quantity_requested": 10,
            "priority": "low",
            "status": "pending"
        }
    ]
    
    for request in restock_requests:
        try:
            response = requests.post(
                f"{SERVICES['logistics']}/restock-requests",
                json=request,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 201:
                print(f"✅ Created restock request for product {request['product_id']}")
            else:
                print(f"⚠️ Failed to create restock request: {response.text}")
        except Exception as e:
            print(f"❌ Error creating restock request: {e}")

def main():
    """Fonction principale"""
    print("🚀 Starting data initialization for all microservices...")
    
    # Attendre que tous les services soient prêts
    all_ready = True
    for service_name, url in SERVICES.items():
        if not wait_for_service(url, service_name):
            all_ready = False
    
    if not all_ready:
        print("❌ Some services are not ready. Please check your docker-compose setup.")
        return
    
    print("\n✅ All services are ready! Starting data initialization...")
    
    # Initialiser les données dans l'ordre des dépendances
    init_customer_service()
    init_store_service()
    init_product_service()
    init_sales_service()
    init_logistics_service()
    
    print("\n🎉 Data initialization completed!")
    print("\n📋 Summary of created data:")
    print("- 7 users (admin, manager, product_manage, logistics, 3 clients)")
    print("- 5 stores (4 supermarchés + 1 centre logistique)")
    print("- 25 products répartis en 5 catégories principales:")
    print("  • Alimentaire (8 produits): fruits/légumes, laitiers, viandes, secs")
    print("  • Électroménager (4 produits): cuisine, ménage")
    print("  • Vêtements (4 produits): hauts, bas, chaussures")
    print("  • Livres (3 produits): roman, cuisine, guide")
    print("  • Maison (6 produits): cuisine, salle de bain, éclairage, déco")
    print("- 2 sample sales")
    print("- 3 demandes de réapprovisionnement")
    print("\n🔑 Default login credentials:")
    print("- Admin: admin@supermarche.com / admin123")
    print("- Manager: manager@supermarche.com / manager123")
    print("- Product Manager: product@supermarche.com / product123")
    print("- Logistics: logistics@supermarche.com / logistics123")
    print("- Client: client1@example.com / client123")
    print("\n🏪 Store Types:")
    print("- 4 SuperMarchés (type: retail)")
    print("- 1 Centre Logistique (type: warehouse)")

if __name__ == "__main__":
    main() 