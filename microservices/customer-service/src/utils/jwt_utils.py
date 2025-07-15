"""
JWT Token utilities for authentication with roles
"""

import jwt
import datetime
from functools import wraps
from flask import request, jsonify, current_app
import os

# Configuration JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'supermarcher_jwt_secret_2024')
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_DELTA = datetime.timedelta(hours=24)

def generate_jwt_token(user_id: int, email: str, role: str) -> str:
    """
    Génère un token JWT avec les informations utilisateur et le rôle
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'exp': datetime.datetime.utcnow() + JWT_EXPIRATION_DELTA,
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    """
    Décode un token JWT et retourne les informations utilisateur
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise Exception("Token expiré")
    except jwt.InvalidTokenError:
        raise Exception("Token invalide")

def jwt_required(f):
    """
    Décorateur pour protéger les routes avec JWT
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header:
            try:
                # Format: "Bearer <token>"
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Format d\'autorisation invalide'}), 401
        
        if not token:
            return jsonify({'error': 'Token manquant'}), 401
        
        try:
            payload = decode_jwt_token(token)
            request.current_user = payload
        except Exception as e:
            return jsonify({'error': str(e)}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def jwt_role_required(required_roles: list):
    """
    Décorateur pour protéger les routes avec JWT et vérifier les rôles
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            auth_header = request.headers.get('Authorization')
            
            if auth_header:
                try:
                    token = auth_header.split(" ")[1]
                except IndexError:
                    return jsonify({'error': 'Format d\'autorisation invalide'}), 401
            
            if not token:
                return jsonify({'error': 'Token manquant'}), 401
            
            try:
                payload = decode_jwt_token(token)
                user_role = payload.get('role')
                
                if user_role not in required_roles:
                    return jsonify({'error': 'Accès refusé - rôle insuffisant'}), 403
                
                request.current_user = payload
            except Exception as e:
                return jsonify({'error': str(e)}), 401
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
