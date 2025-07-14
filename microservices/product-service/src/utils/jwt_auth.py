"""
Module partagé pour l'authentification JWT entre les microservices
"""
import jwt
from functools import wraps
from flask import request, jsonify
from enum import Enum
import os


class UserRole(Enum):
    ADMIN = "admin"
    GESTIONNAIRE = "gestionnaire"
    RESPONSABLE_PRODUIT = "responsable_produit"
    RESPONSABLE_LOGISTIQUE = "responsable_logistique"
    EMPLOYE_MAGASIN = "employe_magasin"
    CLIENT = "client"


class JWTValidator:
    def __init__(self, secret_key=None):
        self.secret_key = secret_key or os.getenv('JWT_SECRET_KEY', 'your-jwt-secret-key-here')
    
    def decode_token(self, token):
        """Décoder et valider un token JWT"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def extract_token_from_request(self, request):
        """Extraire le token JWT de la requête"""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return None
        
        return parts[1]
    
    def validate_role(self, user_role, required_roles):
        """Valider si l'utilisateur a les rôles requis"""
        if not isinstance(required_roles, list):
            required_roles = [required_roles]
        
        try:
            role_enum = UserRole(user_role)
            
            # Admin a accès à tout
            if role_enum == UserRole.ADMIN:
                return True
            
            # Vérifier les rôles spécifiques
            for required_role in required_roles:
                if isinstance(required_role, str):
                    required_role = UserRole(required_role)
                if role_enum == required_role:
                    return True
            
            return False
        except ValueError:
            return False


# Instance globale
jwt_validator = JWTValidator()


def jwt_required(allowed_roles=None):
    """
    Décorateur pour valider les tokens JWT dans les microservices
    
    Args:
        allowed_roles: Liste des rôles autorisés (str ou UserRole)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = jwt_validator.extract_token_from_request(request)
            if not token:
                return jsonify({'error': 'Token JWT manquant'}), 401
            
            payload = jwt_validator.decode_token(token)
            if not payload:
                return jsonify({'error': 'Token JWT invalide ou expiré'}), 401
            
            # Vérifier les rôles si spécifiés
            if allowed_roles:
                user_role = payload.get('role')
                if not user_role:
                    return jsonify({'error': 'Rôle manquant dans le token'}), 401
                
                if not jwt_validator.validate_role(user_role, allowed_roles):
                    return jsonify({'error': 'Permissions insuffisantes'}), 403
            
            # Ajouter les informations utilisateur au contexte
            request.current_user = {
                'user_id': payload.get('user_id'),
                'email': payload.get('email'),
                'role': payload.get('role')
            }
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Décorateur pour les routes nécessitant le rôle admin"""
    return jwt_required([UserRole.ADMIN])(f)


def management_required(f):
    """Décorateur pour les routes nécessitant admin ou gestionnaire"""
    return jwt_required([UserRole.ADMIN, UserRole.GESTIONNAIRE])(f)


def responsable_produit_required(f):
    """Décorateur pour les routes nécessitant responsable produit"""
    return jwt_required([UserRole.ADMIN, UserRole.GESTIONNAIRE, UserRole.RESPONSABLE_PRODUIT])(f)


def responsable_logistique_required(f):
    """Décorateur pour les routes nécessitant responsable logistique"""
    return jwt_required([UserRole.ADMIN, UserRole.GESTIONNAIRE, UserRole.RESPONSABLE_LOGISTIQUE])(f)


def employe_magasin_required(f):
    """Décorateur pour les routes nécessitant employé magasin"""
    return jwt_required([UserRole.ADMIN, UserRole.GESTIONNAIRE, UserRole.EMPLOYE_MAGASIN])(f)


def authenticated_required(f):
    """Décorateur pour les routes nécessitant juste une authentification"""
    return jwt_required()(f)
