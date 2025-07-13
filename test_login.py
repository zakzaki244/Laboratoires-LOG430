#!/usr/bin/env python3
import requests
import sys

# Test de connexion directe au service customer-service
def test_customer_service():
    url = "http://10.194.32.174:5005/api/customers/login"
    data = {"email": "admin@test.com", "password": "admin123"}
    
    try:
        response = requests.post(url, json=data, timeout=10)
        print(f"Customer Service Direct Test:")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print("-" * 50)
        return response.status_code == 200
    except Exception as e:
        print(f"Customer Service Error: {e}")
        return False

# Test de connexion via l'API Gateway
def test_api_gateway():
    url = "http://10.194.32.174:5000/login"
    data = {"username": "admin", "password": "admin123"}
    
    try:
        session = requests.Session()
        response = session.post(url, data=data, timeout=10)
        print(f"API Gateway Test:")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        # Chercher les messages d'erreur ou de succès
        if "Erreur de connexion" in response.text:
            print("❌ Erreur de connexion détectée")
            # Extraire le message d'erreur
            import re
            error_match = re.search(r'Erreur de connexion: ([^<]+)', response.text)
            if error_match:
                print(f"Message d'erreur: {error_match.group(1)}")
        elif "Connexion réussie" in response.text:
            print("✅ Connexion réussie!")
        
        # Tester l'accès à la page d'accueil après connexion
        home_response = session.get("http://10.194.32.174:5000/")
        if "Déconnexion" in home_response.text or "logout" in home_response.text.lower():
            print("✅ Session active - utilisateur connecté")
            return True
        else:
            print("❌ Session inactive - utilisateur non connecté")
        
        print("-" * 50)
        return response.status_code == 302  # Redirection après connexion réussie
    except Exception as e:
        print(f"API Gateway Error: {e}")
        return False

# Test de connexion via nginx
def test_nginx():
    url = "http://10.194.32.174/login"
    data = {"username": "admin", "password": "admin123"}
    
    try:
        response = requests.post(url, data=data, timeout=10, allow_redirects=False)
        print(f"Nginx Test:")
        print(f"URL: {url}")
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response: {response.text[:500]}...")
        print("-" * 50)
        return response.status_code in [200, 302]
    except Exception as e:
        print(f"Nginx Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing E-Commerce Login System")
    print("=" * 50)
    
    # Test chaque composant
    customer_ok = test_customer_service()
    api_gateway_ok = test_api_gateway()
    nginx_ok = test_nginx()
    
    print(f"Results:")
    print(f"Customer Service: {'✓' if customer_ok else '✗'}")
    print(f"API Gateway: {'✓' if api_gateway_ok else '✗'}")
    print(f"Nginx: {'✓' if nginx_ok else '✗'}")
    
    if customer_ok and api_gateway_ok and nginx_ok:
        print("\n🎉 All tests passed! Login system is working.")
    else:
        print("\n❌ Some tests failed. Check the logs above.")
