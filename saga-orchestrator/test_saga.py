#!/usr/bin/env python3
"""
Script de test simple pour la Saga Orchestrator
Usage: python test_saga.py
"""

import requests
import json
import time

def test_saga_basic():
    """Test basique de la Saga orchestrator"""
    
    print("🧪 Test basique de la Saga Orchestrator")
    print("=" * 50)
    
    # URL du service
    base_url = "http://localhost:5007"
    
    # Test de santé
    print("1. Test de santé du service...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("✅ Service en bonne santé")
        else:
            print(f"❌ Service non disponible: {health_response.status_code}")
            return
    except requests.RequestException as e:
        print(f"❌ Impossible de contacter le service: {e}")
        return
    
    # Test de création de Saga
    print("\n2. Test de création de Saga...")
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
    
    try:
        response = requests.post(f"{base_url}/api/saga/order", json=order_data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            order_id = result.get('order_id')
            print(f"✅ Saga créée avec succès")
            print(f"   Order ID: {order_id}")
            print(f"   État: {result.get('state')}")
            print(f"   Message: {result.get('message')}")
            
            # Test de récupération du statut
            print("\n3. Test de récupération du statut...")
            status_response = requests.get(f"{base_url}/api/saga/{order_id}/status", timeout=10)
            
            if status_response.status_code == 200:
                saga_status = status_response.json()
                print(f"✅ Statut récupéré")
                print(f"   État actuel: {saga_status.get('current_state')}")
                print(f"   Nombre d'événements: {len(saga_status.get('events', []))}")
                
                # Afficher les événements
                print("\n   📋 Événements:")
                for i, event in enumerate(saga_status.get('events', []), 1):
                    print(f"   {i}. {event.get('event')} -> {event.get('state')}")
                    
            else:
                print(f"❌ Erreur lors de la récupération du statut: {status_response.status_code}")
                
        elif response.status_code == 400:
            result = response.json()
            print(f"⚠️ Saga échouée (comportement attendu pour certains tests)")
            print(f"   Order ID: {result.get('order_id')}")
            print(f"   État: {result.get('state')}")
            print(f"   Erreur: {result.get('error')}")
            
        else:
            print(f"❌ Erreur inattendue: {response.status_code}")
            print(response.text)
            
    except requests.RequestException as e:
        print(f"❌ Erreur de communication: {e}")
    
    # Test des métriques
    print("\n4. Test des métriques Prometheus...")
    try:
        metrics_response = requests.get(f"{base_url}/metrics", timeout=5)
        if metrics_response.status_code == 200:
            print("✅ Métriques disponibles")
            # Chercher les métriques de Saga
            metrics_text = metrics_response.text
            if "saga_total" in metrics_text:
                print("   Métriques Saga trouvées")
            if "saga_duration_seconds" in metrics_text:
                print("   Métriques de durée trouvées")
        else:
            print(f"❌ Erreur métriques: {metrics_response.status_code}")
    except requests.RequestException as e:
        print(f"❌ Erreur métriques: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test terminé")

if __name__ == "__main__":
    test_saga_basic() 