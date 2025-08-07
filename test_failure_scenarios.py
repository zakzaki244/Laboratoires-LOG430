#!/usr/bin/env python3
"""
Script de test pour les scénarios d'échec de la Saga
Laboratoire 6 - LOG430
"""

import requests
import time
import json
import sys

SAGA_URL = "http://localhost:5006"

def print_header(title):
    """Affiche un en-tête"""
    print(f"\n{'='*60}")
    print(f" {title}")
    print(f"{'='*60}")

def print_test(test_name):
    """Affiche le nom du test"""
    print(f"\n🧪 Test: {test_name}")

def print_success(message):
    """Affiche un message de succès"""
    print(f"✅ {message}")

def print_error(message):
    """Affiche un message d'erreur"""
    print(f"❌ {message}")

def print_info(message):
    """Affiche un message d'information"""
    print(f"ℹ️  {message}")

def check_saga_service():
    """Vérifie que le service saga est disponible"""
    try:
        response = requests.get(f"{SAGA_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("Service Saga Orchestrator disponible")
            return True
        else:
            print_error(f"Service indisponible (Status: {response.status_code})")
            return False
    except requests.exceptions.RequestException as e:
        print_error(f"Impossible de joindre le service: {e}")
        return False

def test_stock_insufficient():
    """Test: Stock insuffisant"""
    print_test("Stock Insuffisant")
    
    payload = {
        "customer_id": "1",
        "items": [
            {"product_id": 1, "quantity": 999, "price": 29.99}
        ]
    }
    
    try:
        response = requests.post(f"{SAGA_URL}/api/saga/order", 
                               json=payload, timeout=10)
        result = response.json()
        
        print_info(f"Réponse: {json.dumps(result, indent=2)}")
        
        # Vérifications
        if result.get("success") == False and result.get("state") == "failed":
            print_success("Test réussi: Stock insuffisant détecté correctement")
            return True
        else:
            print_error(f"Test échoué: Réponse inattendue")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur de requête: {e}")
        return False
    except json.JSONDecodeError as e:
        print_error(f"Erreur de parsing JSON: {e}")
        return False

def test_invalid_customer():
    """Test: Client invalide"""
    print_test("Client Invalide")
    
    payload = {
        "customer_id": "999",  # Client qui n'existe pas
        "items": [
            {"product_id": 1, "quantity": 1, "price": 29.99}
        ]
    }
    
    try:
        response = requests.post(f"{SAGA_URL}/api/saga/order", 
                               json=payload, timeout=10)
        result = response.json()
        
        print_info(f"Réponse: {json.dumps(result, indent=2)}")
        
        if result.get("success") == False:
            print_success("Test réussi: Client invalide détecté")
            return True
        else:
            print_error("Test échoué: Client invalide non détecté")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur de requête: {e}")
        return False

def test_invalid_product():
    """Test: Produit invalide"""
    print_test("Produit Invalide")
    
    payload = {
        "customer_id": "1",
        "items": [
            {"product_id": 999, "quantity": 1, "price": 29.99}  # Produit inexistant
        ]
    }
    
    try:
        response = requests.post(f"{SAGA_URL}/api/saga/order", 
                               json=payload, timeout=10)
        result = response.json()
        
        print_info(f"Réponse: {json.dumps(result, indent=2)}")
        
        if result.get("success") == False:
            print_success("Test réussi: Produit invalide détecté")
            return True
        else:
            print_error("Test échoué: Produit invalide non détecté")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur de requête: {e}")
        return False

def test_negative_price():
    """Test: Prix négatif (échec de paiement)"""
    print_test("Prix Négatif - Échec de Paiement")
    
    payload = {
        "customer_id": "1",
        "items": [
            {"product_id": 1, "quantity": 1, "price": -10.00}  # Prix négatif
        ]
    }
    
    try:
        response = requests.post(f"{SAGA_URL}/api/saga/order", 
                               json=payload, timeout=10)
        result = response.json()
        
        print_info(f"Réponse: {json.dumps(result, indent=2)}")
        
        # Ce test peut réussir (saga failed) ou échouer selon l'implémentation
        if result.get("success") == False:
            if result.get("state") == "cancelled":
                print_success("Test réussi: Compensation exécutée après échec de paiement")
            elif result.get("state") == "failed":
                print_success("Test réussi: Échec de paiement détecté")
            else:
                print_error(f"État inattendu: {result.get('state')}")
                return False
            return True
        else:
            print_error("Test échoué: Prix négatif accepté")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur de requête: {e}")
        return False

def test_malformed_payload():
    """Test: Payload malformé"""
    print_test("Payload Malformé")
    
    payload = {
        "customer_id": "1",
        # items manquant
    }
    
    try:
        response = requests.post(f"{SAGA_URL}/api/saga/order", 
                               json=payload, timeout=10)
        
        if response.status_code >= 400:
            print_success(f"Test réussi: Payload malformé rejeté (Status: {response.status_code})")
            return True
        else:
            print_error("Test échoué: Payload malformé accepté")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur de requête: {e}")
        return False

def test_successful_order():
    """Test: Commande réussie (pour vérifier que le service fonctionne)"""
    print_test("Commande Réussie (Contrôle)")
    
    payload = {
        "customer_id": "1",
        "items": [
            {"product_id": 1, "quantity": 1, "price": 29.99}
        ]
    }
    
    try:
        response = requests.post(f"{SAGA_URL}/api/saga/order", 
                               json=payload, timeout=10)
        result = response.json()
        
        print_info(f"Réponse: {json.dumps(result, indent=2)}")
        
        if result.get("success") == True and result.get("state") == "confirmed":
            print_success("Test de contrôle réussi: Commande normale fonctionne")
            return True
        else:
            print_error("Test de contrôle échoué: Le service ne fonctionne pas correctement")
            return False
            
    except requests.exceptions.RequestException as e:
        print_error(f"Erreur de requête: {e}")
        return False

def generate_load_test():
    """Génère du trafic pour observer les métriques"""
    print_test("Génération de Trafic pour Métriques")
    
    success_count = 0
    failure_count = 0
    
    # Créer un mélange de commandes réussies et échouées
    test_cases = [
        {"customer_id": "1", "items": [{"product_id": 1, "quantity": 1, "price": 29.99}]},  # Succès
        {"customer_id": "1", "items": [{"product_id": 1, "quantity": 999, "price": 29.99}]}, # Échec stock
        {"customer_id": "2", "items": [{"product_id": 2, "quantity": 1, "price": 49.99}]},  # Succès
        {"customer_id": "1", "items": [{"product_id": 1, "quantity": 1, "price": -10.00}]}, # Échec prix
    ]
    
    for i in range(20):  # 20 requêtes
        payload = test_cases[i % len(test_cases)]
        
        try:
            response = requests.post(f"{SAGA_URL}/api/saga/order", 
                                   json=payload, timeout=10)
            result = response.json()
            
            if result.get("success"):
                success_count += 1
                print(".", end="", flush=True)
            else:
                failure_count += 1
                print("x", end="", flush=True)
                
        except requests.exceptions.RequestException:
            failure_count += 1
            print("x", end="", flush=True)
        
        time.sleep(0.2)  # Pause entre requêtes
    
    print(f"\nRésultats du test de charge:")
    print(f"  Succès: {success_count}")
    print(f"  Échecs: {failure_count}")
    print(f"  Total: {success_count + failure_count}")

def main():
    """Fonction principale"""
    print_header("TESTS DE SCÉNARIOS D'ÉCHEC - SAGA ORCHESTRATOR")
    
    # Vérifier la disponibilité du service
    if not check_saga_service():
        print_error("Service Saga non disponible. Arrêt des tests.")
        sys.exit(1)
    
    # Compteurs de tests
    total_tests = 0
    passed_tests = 0
    
    # Exécuter les tests
    tests = [
        test_successful_order,       # Test de contrôle d'abord
        test_stock_insufficient,
        test_invalid_customer,
        test_invalid_product,
        test_negative_price,
        test_malformed_payload,
    ]
    
    for test_func in tests:
        total_tests += 1
        if test_func():
            passed_tests += 1
        time.sleep(1)  # Pause entre tests
    
    # Test de charge (optionnel)
    print_test("Test de Charge (Optionnel)")
    response = input("Voulez-vous exécuter le test de charge? (y/n): ")
    if response.lower() in ['y', 'yes', 'o', 'oui']:
        generate_load_test()
    
    # Résultats finaux
    print_header("RÉSULTATS DES TESTS")
    print(f"Tests passés: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print_success("🎉 Tous les tests sont passés!")
    else:
        print_error(f"❌ {total_tests - passed_tests} test(s) ont échoué")
    
    # Informations pour les métriques
    print(f"\nPour consulter les métriques:")
    print(f"  Prometheus: http://localhost:9090")
    print(f"  Grafana: http://localhost:3000")
    print(f"  Métriques Saga: http://localhost:5006/metrics")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\nTests interrompus par l'utilisateur")
        sys.exit(0)
