"""
JWT utilities for API Gateway
Module partagé pour l'authentification JWT dans l'API Gateway
"""

import jwt
import datetime
import os
from functools import wraps
from flask import request, jsonify, session
import requests
import logging

# Configuration JWT partagée
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'supermarcher_jwt_secret_2024')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=24)

# Configuration des services
CUSTOMER_SERVICE_URL = os.getenv('CUSTOMER_SERVICE_URL', 'http://customer-service:5005')
API_TOKEN = "Supermarcher22102002"

logger = logging.getLogger(__name__)

def verify_jwt_token(token: str) -> dict:
    """Vérifie et décode un token JWT"""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token JWT expiré")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Token JWT invalide")
        return None

def extract_jwt_from_request(request) -> str:
    """Extrait le token JWT de la requête"""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    parts = auth_header.split()
    if parts[0].lower() != 'bearer' or len(parts) != 2:
        return None
    
    return parts[1]

def validate_user_role(user_role: str, required_roles: list) -> bool:
    """Valide si l'utilisateur a les rôles requis"""
    if not isinstance(required_roles, list):
        required_roles = [required_roles]
    
    # Admin a accès à tout
    if user_role == 'admin':
        return True
    
    return user_role in required_roles

def jwt_or_session_required(allowed_roles=None):
    """
    Décorateur hybride qui accepte l'authentification JWT ou session
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérifier d'abord si l'utilisateur est connecté via session
            if 'user_id' in session:
                user_role = session.get('role')
                if allowed_roles and user_role not in allowed_roles:
                    return jsonify({'error': 'Accès refusé - rôle insuffisant'}), 403
                return f(*args, **kwargs)
            
            # Sinon, vérifier le token JWT
            token = extract_jwt_from_request(request)
            if not token:
                return jsonify({'error': 'Authentification requise'}), 401
            
            payload = verify_jwt_token(token)
            if not payload:
                return jsonify({'error': 'Token JWT invalide ou expiré'}), 401
            
            # Vérifier les rôles si spécifiés
            if allowed_roles:
                user_role = payload.get('role')
                if not validate_user_role(user_role, allowed_roles):
                    return jsonify({'error': 'Accès refusé - rôle insuffisant'}), 403
            
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
    """Décorateur pour les routes admin uniquement"""
    return jwt_or_session_required(['admin'])(f)

def management_required(f):
    """Décorateur pour les routes de gestion (admin, gestionnaire)"""
    return jwt_or_session_required(['admin', 'gestionnaire'])(f)

def responsable_produit_required(f):
    """Décorateur pour les routes responsable produit"""
    return jwt_or_session_required(['admin', 'gestionnaire', 'responsable_produit'])(f)

def authenticated_required(f):
    """Décorateur pour les routes nécessitant juste une authentification"""
    return jwt_or_session_required()(f)
