import requests
import json
import time

def test_saga_success():
    """Test du succès d'une Saga de commande complète"""
    
    # URL du saga orchestrator
    base_url = "http://localhost:5007"
    
    # Données de test pour une commande
    order_data = {
        "customer_id": "1",
        "items": [
            {
                "product_id": 1,
                "quantity": 2,
                "price": 29.99
            },
            {
                "product_id": 2,
                "quantity": 1,
                "price": 49.99
            }
        ]
    }
    
    print("🧪 Test: Saga de commande - Cas de succès")
    print("=" * 50)
    
    # Étape 1: Créer et exécuter la Saga
    print("1. Création et exécution de la Saga...")
    response = requests.post(f"{base_url}/api/saga/order", json=order_data)
    
    if response.status_code == 200:
        result = response.json()
        order_id = result.get('order_id')
        print(f"✅ Saga créée avec succès - Order ID: {order_id}")
        print(f"   État final: {result.get('state')}")
        print(f"   Message: {result.get('message')}")
        
        # Étape 2: Vérifier le statut de la Saga
        print("\n2. Vérification du statut de la Saga...")
        status_response = requests.get(f"{base_url}/api/saga/{order_id}/status")
        
        if status_response.status_code == 200:
            saga_status = status_response.json()
            print(f"✅ Statut récupéré avec succès")
            print(f"   État actuel: {saga_status.get('current_state')}")
            print(f"   Nombre d'événements: {len(saga_status.get('events', []))}")
            
            # Afficher les événements
            print("\n   📋 Événements de la Saga:")
            for i, event in enumerate(saga_status.get('events', []), 1):
                print(f"   {i}. {event.get('event')} -> {event.get('state')}")
            
        else:
            print(f"❌ Erreur lors de la récupération du statut: {status_response.status_code}")
            print(status_response.text)
            
    else:
        print(f"❌ Erreur lors de la création de la Saga: {response.status_code}")
        print(response.text)
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")

if __name__ == "__main__":
    test_saga_success() 