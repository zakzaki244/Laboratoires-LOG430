#!/usr/bin/env python3
"""
Script de vérification de la synchronisation des clés JWT entre les microservices
"""

import sys
import os
sys.path.append('/Users/boujettioua/Desktop/ETS école d\'ingénieur /ETS-Cours-3ème année/Session 9/LOG430/Laboratoires-LOG430-1/microservices')

def check_customer_service_jwt():
    """Vérifier la clé JWT du customer-service"""
    try:
        sys.path.append('/Users/boujettioua/Desktop/ETS école d\'ingénieur /ETS-Cours-3ème année/Session 9/LOG430/Laboratoires-LOG430-1/microservices/customer-service')
        from src.utils.jwt_utils import JWT_SECRET_KEY
        return JWT_SECRET_KEY
    except ImportError as e:
        print(f"❌ Erreur d'import customer-service: {e}")
        return None

def check_product_service_jwt():
    """Vérifier la clé JWT du product-service"""
    try:
        sys.path.append('/Users/boujettioua/Desktop/ETS école d\'ingénieur /ETS-Cours-3ème année/Session 9/LOG430/Laboratoires-LOG430-1/microservices/product-service')
        from src.utils.jwt_auth import JWTValidator
        validator = JWTValidator()
        return validator.secret_key
    except ImportError as e:
        print(f"❌ Erreur d'import product-service: {e}")
        return None

def check_shared_module_jwt():
    """Vérifier la clé JWT du module partagé"""
    try:
        sys.path.append('/Users/boujettioua/Desktop/ETS école d\'ingénieur /ETS-Cours-3ème année/Session 9/LOG430/Laboratoires-LOG430-1/microservices/shared')
        from jwt_auth_new import JWT_SECRET_KEY
        return JWT_SECRET_KEY
    except ImportError as e:
        print(f"❌ Erreur d'import module partagé: {e}")
        return None

def test_token_interoperability():
    """Tester l'interopérabilité des tokens entre les services"""
    try:
        # Import des modules nécessaires
        sys.path.append('/Users/boujettioua/Desktop/ETS école d\'ingénieur /ETS-Cours-3ème année/Session 9/LOG430/Laboratoires-LOG430-1/microservices/customer-service')
        sys.path.append('/Users/boujettioua/Desktop/ETS école d\'ingénieur /ETS-Cours-3ème année/Session 9/LOG430/Laboratoires-LOG430-1/microservices/product-service')
        sys.path.append('/Users/boujettioua/Desktop/ETS école d\'ingénieur /ETS-Cours-3ème année/Session 9/LOG430/Laboratoires-LOG430-1/microservices/shared')
        
        # Générer un token avec customer-service
        from src.utils.jwt_utils import generate_jwt_token
        test_token = generate_jwt_token(1, "test@example.com", "client")
        
        # Valider le token avec product-service
        from src.utils.jwt_auth import JWTValidator
        validator = JWTValidator()
        payload = validator.decode_token(test_token)
        
        if payload:
            print("✅ Token généré par customer-service validé par product-service")
            print(f"   Payload: {payload}")
            return True
        else:
            print("❌ Token généré par customer-service REJETÉ par product-service")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test d'interopérabilité: {e}")
        return False

def main():
    """Fonction principale"""
    print("=== Vérification de la synchronisation des clés JWT ===")
    
    # Vérifier les clés JWT
    customer_key = check_customer_service_jwt()
    product_key = check_product_service_jwt()
    shared_key = check_shared_module_jwt()
    
    print(f"\n🔑 Clés JWT trouvées:")
    print(f"Customer Service: {customer_key}")
    print(f"Product Service:  {product_key}")
    print(f"Module Partagé:   {shared_key}")
    
    # Vérifier la synchronisation
    keys = [customer_key, product_key, shared_key]
    keys = [k for k in keys if k is not None]
    
    if len(set(keys)) == 1:
        print(f"\n✅ Toutes les clés JWT sont synchronisées: {keys[0]}")
    else:
        print(f"\n❌ Les clés JWT ne sont PAS synchronisées!")
        print(f"   Clés différentes trouvées: {set(keys)}")
    
    # Test d'interopérabilité
    print(f"\n🔄 Test d'interopérabilité des tokens:")
    test_token_interoperability()
    
    print(f"\n🎯 Résumé:")
    print(f"- Customer Service utilise: {customer_key}")
    print(f"- Product Service utilise:  {product_key}")
    print(f"- Module Partagé utilise:   {shared_key}")
    
    if len(set(keys)) == 1:
        print(f"✅ Synchronisation réussie!")
    else:
        print(f"❌ Synchronisation échouée - clés différentes!")

if __name__ == "__main__":
    main()
