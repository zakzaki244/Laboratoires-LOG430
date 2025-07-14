"""
Décorateurs pour la protection des routes par rôle dans l'API Gateway
"""

from functools import wraps
from flask import session, request, jsonify, redirect, url_for
import requests
import os

# Configuration
SERVICES = {
    'customer': os.getenv('CUSTOMER_SERVICE_URL', 'http://customer-service:5005'),
}
API_TOKEN = "Supermarcher22102002"

def role_required(required_roles: list):
    """
    Décorateur pour protéger les routes par rôle
    Usage: @role_required(['admin', 'gestionnaire'])
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Vérifier si l'utilisateur est connecté
            if 'user_id' not in session:
                if request.is_json:
                    return jsonify({'error': 'Authentification requise'}), 401
                return redirect(url_for('login'))
            
            user_role = session.get('user_role')
            
            # Vérifier si l'utilisateur a un rôle autorisé
            if user_role not in required_roles:
                if request.is_json:
                    return jsonify({'error': 'Accès refusé - rôle insuffisant'}), 403
                return jsonify({'error': 'Accès refusé - rôle insuffisant'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Décorateur pour les routes administrateur uniquement"""
    return role_required(['admin'])(f)

def gestionnaire_required(f):
    """Décorateur pour les routes gestionnaire et admin"""
    return role_required(['admin', 'gestionnaire'])(f)

def responsable_produit_required(f):
    """Décorateur pour les routes responsable produit, gestionnaire et admin"""
    return role_required(['admin', 'gestionnaire', 'responsable_produit'])(f)

def responsable_logistique_required(f):
    """Décorateur pour les routes responsable logistique, gestionnaire et admin"""
    return role_required(['admin', 'gestionnaire', 'responsable_logistique'])(f)

def employe_magasin_required(f):
    """Décorateur pour les routes employé magasin, gestionnaire et admin"""
    return role_required(['admin', 'gestionnaire', 'employe_magasin'])(f)

def management_required(f):
    """Décorateur pour les routes de gestion (admin, gestionnaire)"""
    return role_required(['admin', 'gestionnaire'])(f)

def authenticated_required(f):
    """Décorateur pour les routes nécessitant une authentification simple"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'error': 'Authentification requise'}), 401
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
