import requests
import json
import time

def test_saga_failure():
    """Test de la gestion des échecs dans la Saga"""
    
    # URL du saga orchestrator
    base_url = "http://localhost:5007"
    
    print("🧪 Test: Saga de commande - Cas d'échec")
    print("=" * 50)
    
    # Test 1: Échec de vérification de stock (produit inexistant)
    print("1. Test: Échec de vérification de stock...")
    order_data_stock_failure = {
        "customer_id": "1",
        "items": [
            {
                "product_id": 999,  # Produit inexistant
                "quantity": 1,
                "price": 29.99
            }
        ]
    }
    
    response = requests.post(f"{base_url}/api/saga/order", json=order_data_stock_failure)
    
    if response.status_code == 400:
        result = response.json()
        order_id = result.get('order_id')
        print(f"✅ Échec de stock détecté correctement")
        print(f"   Order ID: {order_id}")
        print(f"   État final: {result.get('state')}")
        print(f"   Erreur: {result.get('error')}")
        
        # Vérifier le statut
        status_response = requests.get(f"{base_url}/api/saga/{order_id}/status")
        if status_response.status_code == 200:
            saga_status = status_response.json()
            print(f"   Événements: {len(saga_status.get('events', []))}")
    else:
        print(f"❌ Test d'échec de stock échoué: {response.status_code}")
    
    print("\n" + "-" * 30)
    
    # Test 2: Échec de paiement (simulation)
    print("2. Test: Échec de paiement...")
    # Note: Pour tester l'échec de paiement, il faudrait modifier le service de vente
    # pour simuler un échec. Pour l'instant, on teste avec des données valides.
    
    order_data_payment_failure = {
        "customer_id": "1",
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "price": 29.99
            }
        ]
    }
    
    response = requests.post(f"{base_url}/api/saga/order", json=order_data_payment_failure)
    
    if response.status_code == 200:
        result = response.json()
        order_id = result.get('order_id')
        print(f"✅ Saga exécutée avec succès (paiement simulé)")
        print(f"   Order ID: {order_id}")
        print(f"   État final: {result.get('state')}")
        
        # Vérifier le statut
        status_response = requests.get(f"{base_url}/api/saga/{order_id}/status")
        if status_response.status_code == 200:
            saga_status = status_response.json()
            print(f"   Événements: {len(saga_status.get('events', []))}")
            
            # Afficher les événements
            print("\n   📋 Événements de la Saga:")
            for i, event in enumerate(saga_status.get('events', []), 1):
                print(f"   {i}. {event.get('event')} -> {event.get('state')}")
    else:
        print(f"❌ Test de paiement échoué: {response.status_code}")
        print(response.text)
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")

def test_compensation():
    """Test des mécanismes de compensation"""
    
    base_url = "http://localhost:5007"
    
    print("🧪 Test: Mécanismes de compensation")
    print("=" * 50)
    
    # Créer une Saga qui va échouer
    order_data = {
        "customer_id": "1",
        "items": [
            {
                "product_id": 1,
                "quantity": 1,
                "price": 29.99
            }
        ]
    }
    
    # Exécuter la Saga
    response = requests.post(f"{base_url}/api/saga/order", json=order_data)
    
    if response.status_code == 200:
        result = response.json()
        order_id = result.get('order_id')
        print(f"✅ Saga créée - Order ID: {order_id}")
        
        # Déclencher manuellement les compensations
        print("\n3. Test des compensations manuelles...")
        compensation_response = requests.post(f"{base_url}/api/saga/{order_id}/compensate")
        
        if compensation_response.status_code == 200:
            print("✅ Compensations exécutées avec succès")
        else:
            print(f"❌ Erreur lors des compensations: {compensation_response.status_code}")
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")

if __name__ == "__main__":
    test_saga_failure()
    print("\n")
    test_compensation() 