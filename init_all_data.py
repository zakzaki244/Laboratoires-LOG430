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
    # 'logistics': 'http://10.194.32.174:5007'
}

# Variables globales pour stocker les IDs créés
created_stores = []
created_customers = []
created_products = []

def wait_for_service(url, service_name):
    """Attendre qu'un service soit disponible"""
    max_attempts = 30
    for attempt in range(max_attempts):
        try:
            # Essayer différentes routes selon le service
            if service_name == 'customer':
                response = requests.get(f"{url}/users", timeout=5)
            elif service_name == 'product':
                response = requests.get(f"{url}/products", timeout=5)
            elif service_name == 'store':
                response = requests.get(f"{url}/stores", timeout=5)
            elif service_name == 'sales':
                response = requests.get(f"{url}/sales", timeout=5)
            elif service_name == 'cart':
                response = requests.get(f"{url}/cart", timeout=5)
            elif service_name == 'checkout':
                response = requests.post(f"{url}/checkout", json={}, timeout=5)
            else:
                response = requests.get(f"{url}/", timeout=5)
            
            if response.status_code in [200, 401, 403, 405]:  # 401/403 = service fonctionne mais auth requise
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
            "username": "admin",
            "email": "admin@supermarche.com",
            "password": "admin123",
            "role": "admin"
        },
        {
            "username": "manager",
            "email": "manager@supermarche.com",
            "password": "manager123",
            "role": "manager"
        },
        {
            "username": "product_manager",
            "email": "product@supermarche.com",
            "password": "product123",
            "role": "product_manager"
        },
        {
            "username": "logistics_manager",
            "email": "logistics@supermarche.com",
            "password": "logistics123",
            "role": "logistics"
        },
        {
            "username": "jean_dupont",
            "email": "jean.dupont@example.com",
            "password": "client123",
            "role": "client"
        },
        {
            "username": "marie_martin",
            "email": "client2@example.com",
            "password": "client123",
            "role": "client"
        },
        {
            "username": "pierre_durand",
            "email": "client3@example.com",
            "password": "client123",
            "role": "client"
        },
        {
            "username": "claire_bernard",
            "email": "client4@example.com",
            "password": "client123",
            "role": "client"
        },
        {
            "username": "sophie_moreau",
            "email": "client5@example.com",
            "password": "client123",
            "role": "client"
        }
    ]
    
    global created_customers
    created_customers = []
    
    for customer in customers:
        try:
            response = requests.post(
                f"{SERVICES['customer']}/register",
                json=customer,
                headers={'Content-Type': 'application/json'}
            )
            if response.status_code == 201:
                customer_data = response.json()
                created_customers.append({
                    'id': customer_data.get('id'),
                    'username': customer['username'],
                    'email': customer['email'],
                    'role': customer['role']
                })
                print(f"✅ Created customer: {customer['username']} (ID: {customer_data.get('id')})")
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    if "déjà utilisé" in error_data.get('message', ''):
                        print(f"⚠️ Customer {customer['username']} already exists, skipping...")
                    else:
                        print(f"❌ Failed to create customer {customer['username']}: {error_data.get('message', response.text)}")
                except:
                    print(f"❌ Failed to create customer {customer['username']}: {response.text}")
            else:
                print(f"❌ Failed to create customer {customer['username']} (Status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"❌ Error creating customer {customer['username']}: {e}")

    # Login admin pour obtenir le token
    try:
        login_resp = requests.post(
            f"{SERVICES['customer']}/login",
            json={"email": "admin@supermarche.com", "password": "admin123"},
            headers={'Content-Type': 'application/json'}
        )
        if login_resp.status_code == 200:
            token = login_resp.json().get("token")
            print("✅ Admin login successful, token obtained.")
        else:
            print(f"❌ Admin login failed: {login_resp.text}")
            token = None
    except Exception as e:
        print(f"❌ Error during admin login: {e}")
        token = None
    return token

def init_store_service(headers):
    """Initialiser les magasins"""
    print("\n🏪 Initializing Store Service...")
    
    stores = [
        {
            "name": "SuperMarché Centre-Ville",
            "address": "1000 Rue Sainte-Catherine, Montréal, QC",
            "phone": "514-555-2001",
            "email": "centreville@supermarche.com"
        },
        {
            "name": "SuperMarché Westmount",
            "address": "2000 Avenue Greene, Westmount, QC",
            "phone": "514-555-2002",
            "email": "westmount@supermarche.com"
        },
        {
            "name": "SuperMarché Laval",
            "address": "3000 Boulevard des Laurentides, Laval, QC",
            "phone": "514-555-2003",
            "email": "laval@supermarche.com"
        },
        {
            "name": "SuperMarché Brossard",
            "address": "4000 Boulevard Taschereau, Brossard, QC",
            "phone": "514-555-2004",
            "email": "brossard@supermarche.com"
        },
        {
            "name": "Centre Logistique Principal",
            "address": "5000 Boulevard Industriel, Montréal, QC",
            "phone": "514-555-2005",
            "email": "logistics@supermarche.com"
        }
    ]
    
    global created_stores
    created_stores = []
    
    for store in stores:
        try:
            response = requests.post(
                f"{SERVICES['store']}/stores",
                json=store,
                headers=headers
            )
            if response.status_code == 201:
                store_data = response.json()
                created_stores.append({
                    'id': store_data.get('id'),
                    'name': store['name'],
                    'address': store['address']
                })
                print(f"✅ Created store: {store['name']} (ID: {store_data.get('id')})")
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"⚠️ Store {store['name']} might already exist: {error_data.get('message', response.text)}")
                except:
                    print(f"⚠️ Store {store['name']} creation issue: {response.text}")
            else:
                print(f"❌ Failed to create store {store['name']} (Status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"❌ Error creating store {store['name']}: {e}")
    
    return created_stores

def init_product_service(headers):
    """Initialiser les produits par catégories"""
    print("\n📦 Initializing Product Service...")
    
    # Utiliser les magasins créés précédemment
    global created_stores
    if not created_stores:
        print("⚠️ No stores found, creating products without store association")
        store_ids = [1, 2, 3, 4, 5]  # IDs par défaut
    else:
        store_ids = [store['id'] for store in created_stores]
    
    products = [
        # Fruits et Légumes
        {
            "name": "Pommes Gala (1kg)",
            "description": "Pommes fraîches et juteuses",
            "price": 4.99,
            "quantity_stock": 50,
            "category": "fruits_legumes",
            "store_id": store_ids[0] if store_ids else 1
        },
        {
            "name": "Bananes (1kg)",
            "description": "Bananes biologiques",
            "price": 3.49,
            "quantity_stock": 75,
            "category": "fruits_legumes",
            "store_id": store_ids[0] if store_ids else 1
        },
        {
            "name": "Tomates (500g)",
            "description": "Tomates cerises fraîches",
            "price": 5.99,
            "quantity_stock": 30,
            "category": "fruits_legumes",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0]
        },
        
        # Produits Laitiers
        {
            "name": "Lait 2% (2L)",
            "description": "Lait frais du Québec",
            "price": 4.49,
            "quantity_stock": 40,
            "category": "laitiers",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0]
        },
        {
            "name": "Fromage Cheddar (500g)",
            "description": "Fromage cheddar vieilli",
            "price": 8.99,
            "quantity_stock": 20,
            "category": "laitiers",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0]
        },
        
        # Viandes
        {
            "name": "Poulet Entier (2kg)",
            "description": "Poulet frais du Québec",
            "price": 15.99,
            "quantity_stock": 15,
            "category": "viandes",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0]
        },
        {
            "name": "Saumon Atlantique (500g)",
            "description": "Filet de saumon frais",
            "price": 24.99,
            "quantity_stock": 10,
            "category": "viandes",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0]
        },
        
        # Produits Secs
        {
            "name": "Riz Basmati (2kg)",
            "description": "Riz basmati parfumé",
            "price": 7.99,
            "quantity_stock": 60,
            "category": "secs",
            "store_id": store_ids[3] if len(store_ids) > 3 else store_ids[0]
        },
        {
            "name": "Pâtes Spaghetti (500g)",
            "description": "Pâtes de blé dur",
            "price": 2.49,
            "quantity_stock": 80,
            "category": "secs",
            "store_id": store_ids[3] if len(store_ids) > 3 else store_ids[0]
        },
        
        # Électroménager
        {
            "name": "Mixeur KitchenAid",
            "description": "Mixeur professionnel 5 vitesses",
            "price": 89.99,
            "quantity_stock": 12,
            "category": "electromenager",
            "store_id": store_ids[4] if len(store_ids) > 4 else store_ids[0]
        },
        {
            "name": "Grille-pain Delonghi",
            "description": "Grille-pain 4 fentes",
            "price": 45.99,
            "quantity_stock": 18,
            "category": "electromenager",
            "store_id": store_ids[4] if len(store_ids) > 4 else store_ids[0]
        },
        
        # Vêtements
        {
            "name": "T-shirt Cotton (M)",
            "description": "T-shirt 100% coton bio",
            "price": 24.99,
            "quantity_stock": 35,
            "category": "vetements",
            "store_id": store_ids[0] if store_ids else 1
        },
        {
            "name": "Jean Levi's (32/32)",
            "description": "Jean classique",
            "price": 79.99,
            "quantity_stock": 20,
            "category": "vetements",
            "store_id": store_ids[0] if store_ids else 1
        },
        
        # Livres
        {
            "name": "Harry Potter Tome 1",
            "description": "Harry Potter à l'école des sorciers",
            "price": 29.99,
            "quantity_stock": 25,
            "category": "livres",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0]
        },
        {
            "name": "Cuisine du Québec",
            "description": "Livre de recettes traditionnelles",
            "price": 34.99,
            "quantity_stock": 18,
            "category": "livres",
            "store_id": store_ids[1] if len(store_ids) > 1 else store_ids[0]
        },
        
        # Maison
        {
            "name": "Casserole Le Creuset",
            "description": "Casserole en fonte émaillée",
            "price": 249.99,
            "quantity_stock": 8,
            "category": "maison",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0]
        },
        {
            "name": "Serviettes de Bain (6)",
            "description": "Serviettes 100% coton",
            "price": 49.99,
            "quantity_stock": 22,
            "category": "maison",
            "store_id": store_ids[2] if len(store_ids) > 2 else store_ids[0]
        }
    ]
    
    global created_products
    created_products = []
    
    for product in products:
        try:
            response = requests.post(
                f"{SERVICES['product']}/products",
                json=product,
                headers=headers
            )
            if response.status_code == 201:
                product_data = response.json()
                created_products.append({
                    'id': product_data.get('id'),
                    'name': product['name'],
                    'price': product['price'],
                    'category': product['category'],
                    'store_id': product['store_id']
                })
                print(f"✅ Created product: {product['name']} (ID: {product_data.get('id')})")
            elif response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"⚠️ Product {product['name']} creation issue: {error_data.get('message', response.text)}")
                except:
                    print(f"⚠️ Product {product['name']} creation issue: {response.text}")
            else:
                print(f"❌ Failed to create product {product['name']} (Status {response.status_code}): {response.text}")
        except Exception as e:
            print(f"❌ Error creating product {product['name']}: {e}")
    
    return created_products

def init_sales_service(headers):
    """Initialiser quelques ventes de test"""
    print("\n💰 Initializing Sales Service...")
    
    # Utiliser les données créées précédemment
    global created_customers, created_products
    
    if not created_customers or not created_products:
        print("⚠️ No customers or products found, skipping sales initialization")
        return
    
    # Prendre les clients (pas les admins)
    client_customers = [c for c in created_customers if c['role'] == 'client']
    
    if len(client_customers) < 2 or len(created_products) < 5:
        print("⚠️ Not enough customers or products for sales, skipping")
        return
    
    # Créer quelques ventes de test
    sales = [
        {
            "client_id": client_customers[0]['id'],
            "total": 13.98,  # 2 pommes + 1 lait
            "items": [
                {"product_id": created_products[0]['id'], "quantity": 2, "unit_price": created_products[0]['price']},
                {"product_id": created_products[3]['id'], "quantity": 1, "unit_price": created_products[3]['price']}
            ]
        },
        {
            "client_id": client_customers[1]['id'],
            "total": 32.97,  # 1 saumon + 1 casserole (si disponible)
            "items": [
                {"product_id": created_products[6]['id'], "quantity": 1, "unit_price": created_products[6]['price']},
                {"product_id": created_products[7]['id'], "quantity": 1, "unit_price": created_products[7]['price']}
            ]
        }
    ]
    
    for sale in sales:
        try:
            response = requests.post(
                f"{SERVICES['sales']}/sales",
                json=sale,
                headers=headers
            )
            if response.status_code == 201:
                print(f"✅ Created sale for client {sale['client_id']}: ${sale['total']}")
            else:
                print(f"⚠️ Failed to create sale: {response.text}")
        except Exception as e:
            print(f"❌ Error creating sale: {e}")

def init_logistics_service(headers):
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
                headers=headers
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
    
    admin_token = init_customer_service()
    if not admin_token:
        print("❌ Impossible d'obtenir le token admin, arrêt du script.")
        return
    headers = {'Content-Type': 'application/json', 'Authorization': f'Bearer {admin_token}'}

    # Initialiser les données dans l'ordre des dépendances
    init_store_service(headers)
    init_product_service(headers)
    init_sales_service(headers)
    # init_logistics_service(headers)
    
    print("\n🎉 Data initialization completed!")
    print("\n📋 Summary of created data:")
    print(f"- {len(created_customers)} users (admin, manager, product_manager, logistics, clients)")
    print(f"- {len(created_stores)} stores")
    print(f"- {len(created_products)} products in various categories")
    print("- Sample sales transactions")
    print("\n🔑 Default login credentials:")
    print("- Admin: admin@supermarche.com / admin123")
    print("- Manager: manager@supermarche.com / manager123")
    print("- Product Manager: product@supermarche.com / product123")
    print("- Logistics: logistics@supermarche.com / logistics123")
    print("- Client: client1@example.com / client123")

if __name__ == "__main__":
    main() 