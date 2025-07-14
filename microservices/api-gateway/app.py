from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import requests
import os
from functools import wraps
from prometheus_flask_exporter import PrometheusMetrics
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

# Import des décorateurs d'authentification
from auth_decorators import (
    role_required, admin_required, gestionnaire_required,
    responsable_produit_required, responsable_logistique_required,
    employe_magasin_required, management_required, authenticated_required
)

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here-123456')
metrics = PrometheusMetrics(app)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
limiter.init_app(app)

# Configuration des services
SERVICES = {
    'store': os.getenv('STORE_SERVICE_URL', 'http://store-service:5001'),
    'product': os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:5002'),
    'sales': os.getenv('SALES_SERVICE_URL', 'http://sales-service:5003'),
    'inventory': os.getenv('INVENTORY_SERVICE_URL', 'http://inventory-service:5004'),
    'customer': os.getenv('CUSTOMER_SERVICE_URL', 'http://customer-service:5005'),
    'cart': os.getenv('CART_SERVICE_URL', 'http://cart-service:5006'),
    'checkout': os.getenv('CHECKOUT_SERVICE_URL', 'http://checkout-service:5007')
}

API_TOKEN = "Supermarcher22102002"

# Configuration du logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Unauthorized"}), 401
        token = auth_header.split(" ")[1]
        if token != API_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated

def forward_request(service_name, path, method='GET'):
    """Forwarder les requêtes vers les microservices"""
    try:
        service_url = SERVICES[service_name]
        url = f"{service_url}/{path}"
        logger.info(f"Forwarding {method} request to {url}")
        
        headers = {
            'Authorization': f'Bearer {API_TOKEN}',
            'Content-Type': 'application/json'
        }
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=request.get_json())
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=request.get_json())
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            return jsonify({"error": "Method not supported"}), 405
            
        return response.json() if response.content else {}, response.status_code
        
    except Exception as e:
        logger.error(f"Error forwarding request: {str(e)}")
        return jsonify({"error": f"Service {service_name} unavailable"}), 503

# ========== NOUVEAU SYSTÈME DE CONNEXION SIMPLIFIÉ ==========

# Définition des utilisateurs de test
TEST_USERS = {
    'admin@supermarcher.com': {'password': 'admin123', 'role': 'admin', 'name': 'Admin System'},
    'gestionnaire@supermarcher.com': {'password': 'gestionnaire123', 'role': 'gestionnaire', 'name': 'Gestionnaire Maison Mère'},
    'responsable.produit@supermarcher.com': {'password': 'produit123', 'role': 'responsable_produit', 'name': 'Responsable Produit'},
    'responsable.logistique@supermarcher.com': {'password': 'logistique123', 'role': 'responsable_logistique', 'name': 'Responsable Logistique'},
    'employe.magasin@supermarcher.com': {'password': 'employe123', 'role': 'employe_magasin', 'name': 'Employé Magasin'},
    'client@supermarcher.com': {'password': 'client123', 'role': 'client', 'name': 'Client Test'},
}

def authenticate_user(username, password):
    """Authentifier un utilisateur via le customer-service"""
    try:
        # Essayer d'abord avec l'email direct
        email = username if '@' in username else f"{username}@example.com"
        
        logger.info(f"Attempting to authenticate user: {email}")
        
        # Appel au customer-service
        url = f"{SERVICES['customer']}/api/customers/login"
        response = requests.post(url, 
                               json={'email': email, 'password': password}, 
                               headers={'Authorization': f'Bearer {API_TOKEN}'},
                               timeout=5)
        
        logger.info(f"Customer service response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            customer = data.get('customer', {})
            return {
                'success': True,
                'user': {
                    'id': customer.get('id'),
                    'email': customer.get('email'),
                    'first_name': customer.get('first_name'),
                    'last_name': customer.get('last_name'),
                    'role': customer.get('role'),
                    'store_id': customer.get('store_id')
                }
            }
        else:
            logger.warning(f"Authentication failed for {email}: {response.status_code}")
            return {'success': False, 'error': 'Invalid credentials'}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Customer service unavailable: {str(e)}")
        
        # Fallback vers les utilisateurs de test
        logger.info("Using fallback authentication")
        if username in TEST_USERS:
            test_user = TEST_USERS[username]
            if test_user['password'] == password:
                return {
                    'success': True,
                    'user': {
                        'id': 1,
                        'email': username if '@' in username else f"{username}@example.com",
                        'first_name': test_user['name'].split()[0],
                        'last_name': test_user['name'].split()[1],
                        'role': test_user['role'],
                        'store_id': 1
                    }
                }
        
        return {'success': False, 'error': 'Service unavailable'}
    
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        return {'success': False, 'error': 'Authentication error'}

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion simplifiée"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Nom d\'utilisateur et mot de passe requis', 'error')
            return render_template('login.html')
        
        # Authentification
        auth_result = authenticate_user(username, password)
        
        if auth_result['success']:
            user = auth_result['user']
            
            # Créer la session
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            session['role'] = user['role']
            session['store_id'] = user['store_id']
            session['logged_in'] = True
            
            flash(f'Connexion réussie! Bienvenue {user["first_name"]}', 'success')
            logger.info(f"User {user['email']} logged in successfully with role {user['role']}")
            
            # Redirection selon le rôle
            if user['role'] in ['admin', 'gestionnaire', 'responsable_produit', 'responsable_logistique']:
                return redirect(url_for('admin'))
            elif user['role'] == 'employe_magasin':
                return redirect(url_for('stores'))  # Redirige vers la gestion des magasins
            else:
                return redirect(url_for('index'))  # Clients et autres
        else:
            flash(auth_result['error'], 'error')
            logger.warning(f"Failed login attempt for {username}")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    username = session.get('email', 'Unknown')
    session.clear()
    flash('Déconnexion réussie', 'success')
    logger.info(f"User {username} logged out")
    return redirect(url_for('login'))

def require_login(f):
    """Décorateur pour les routes nécessitant une connexion"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            flash('Vous devez vous connecter pour accéder à cette page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(required_roles):
    """Décorateur pour les routes nécessitant un rôle spécifique"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not session.get('logged_in'):
                flash('Vous devez vous connecter pour accéder à cette page', 'error')
                return redirect(url_for('login'))
            
            user_role = session.get('role')
            if user_role not in required_roles:
                flash('Accès refusé: permissions insuffisantes', 'error')
                return redirect(url_for('index'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ========== DÉCORATEURS SPÉCIFIQUES PAR RÔLE ==========

def require_admin(f):
    """Décorateur pour les routes nécessitant le rôle admin"""
    return require_role(['admin'])(f)

def require_gestionnaire(f):
    """Décorateur pour les routes nécessitant le rôle gestionnaire"""
    return require_role(['admin', 'gestionnaire'])(f)

def require_responsable_produit(f):
    """Décorateur pour les routes nécessitant le rôle responsable produit"""
    return require_role(['admin', 'gestionnaire', 'responsable_produit'])(f)

def require_responsable_logistique(f):
    """Décorateur pour les routes nécessitant le rôle responsable logistique"""
    return require_role(['admin', 'gestionnaire', 'responsable_logistique'])(f)

def require_employe_magasin(f):
    """Décorateur pour les routes nécessitant le rôle employé magasin"""
    return require_role(['admin', 'gestionnaire', 'employe_magasin'])(f)

def require_client(f):
    """Décorateur pour les routes nécessitant le rôle client"""
    return require_role(['admin', 'gestionnaire', 'client'])(f)

def require_management_access(f):
    """Décorateur pour les routes de gestion (admin, gestionnaire, responsables)"""
    return require_role(['admin', 'gestionnaire', 'responsable_produit', 'responsable_logistique'])(f)

# ========== ROUTES PRINCIPALES ==========

@app.route('/')
def index():
    """Page d'accueil"""
    # Statistiques de base pour la page d'accueil
    stats = {
        'total_products': 0,
        'total_stores': 0,
        'total_sales': 0,
        'total_customers': 0
    }
    
    try:
        # Récupération des statistiques basiques
        products_response = requests.get(f"{SERVICES['product']}/api/products", 
                                       headers={'Authorization': f'Bearer {API_TOKEN}'}, 
                                       timeout=2)
        if products_response.status_code == 200:
            products_data = products_response.json()
            stats['total_products'] = len(products_data.get('products', []))
    except:
        pass
    
    try:
        stores_response = requests.get(f"{SERVICES['store']}/api/stores", 
                                     headers={'Authorization': f'Bearer {API_TOKEN}'}, 
                                     timeout=2)
        if stores_response.status_code == 200:
            stores_data = stores_response.json()
            stats['total_stores'] = len(stores_data.get('stores', []))
    except:
        pass
    
    return render_template('index.html', stats=stats)

@app.route('/admin')
@management_required
def admin():
    """Page d'administration"""
    # Récupération des statistiques en temps réel
    dashboard_stats = {
        'services_count': 0,
        'products_count': 0,
        'stores_count': 0,
        'sales_count': 0,
        'services_status': {}
    }
    
    try:
        # Nombre de services actifs
        services_active = 0
        for service_name, service_url in SERVICES.items():
            try:
                response = requests.get(f"{service_url}/health", timeout=2)
                is_active = response.status_code == 200
                dashboard_stats['services_status'][service_name] = is_active
                if is_active:
                    services_active += 1
            except:
                dashboard_stats['services_status'][service_name] = False
        
        dashboard_stats['services_count'] = services_active
        
        # Nombre de produits
        try:
            response = requests.get(f"{SERVICES['product']}/products", 
                                  headers={'Authorization': f'Bearer {API_TOKEN}'},
                                  timeout=3)
            if response.status_code == 200:
                dashboard_stats['products_count'] = len(response.json())
        except:
            pass
        
        # Nombre de magasins
        try:
            response = requests.get(f"{SERVICES['store']}/stores", 
                                  headers={'Authorization': f'Bearer {API_TOKEN}'},
                                  timeout=3)
            if response.status_code == 200:
                dashboard_stats['stores_count'] = len(response.json())
        except:
            pass
        
        # Nombre de ventes (si le service fonctionne)
        try:
            response = requests.get(f"{SERVICES['sales']}/sales", 
                                  headers={'Authorization': f'Bearer {API_TOKEN}'},
                                  timeout=3)
            if response.status_code == 200:
                dashboard_stats['sales_count'] = len(response.json())
        except:
            dashboard_stats['sales_count'] = 28  # Valeur par défaut
        
    except Exception as e:
        logger.error(f"Error loading dashboard stats: {str(e)}")
    
    return render_template('admin.html', dashboard_stats=dashboard_stats)

@app.route('/stores', methods=['GET', 'POST'])
@management_required
def stores():
    """Liste des magasins"""
    if request.method == 'POST':
        # Création d'un nouveau magasin
        try:
            store_data = {
                'name': request.form.get('name'),
                'address': request.form.get('address'),
                'phone': request.form.get('phone', ''),
                'manager': request.form.get('manager', '')
            }
            
            response = requests.post(f"{SERVICES['store']}/stores", 
                                   json=store_data,
                                   headers={'Authorization': f'Bearer {API_TOKEN}'},
                                   timeout=5)
            
            if response.status_code == 201:
                flash('Magasin créé avec succès!', 'success')
            else:
                flash('Erreur lors de la création du magasin', 'error')
                
        except Exception as e:
            logger.error(f"Error creating store: {str(e)}")
            flash('Erreur lors de la création du magasin', 'error')
        
        return redirect(url_for('stores'))
    
    # Affichage de la liste des magasins
    try:
        response = requests.get(f"{SERVICES['store']}/stores", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'},
                              timeout=5)
        stores_data = response.json() if response.status_code == 200 else []
        return render_template('stores.html', stores=stores_data)
    except Exception as e:
        logger.error(f"Error loading stores: {str(e)}")
        flash('Erreur lors du chargement des magasins', 'error')
        return render_template('stores.html', stores=[])

@app.route('/stores/<int:store_id>', methods=['GET', 'POST'])
@require_login
def edit_store(store_id):
    """Éditer un magasin"""
    if request.method == 'POST':
        # Mise à jour du magasin
        try:
            store_data = {
                'name': request.form.get('name'),
                'address': request.form.get('address'),
                'phone': request.form.get('phone', ''),
                'manager': request.form.get('manager', '')
            }
            
            response = requests.put(f"{SERVICES['store']}/stores/{store_id}", 
                                   json=store_data,
                                   headers={'Authorization': f'Bearer {API_TOKEN}'},
                                   timeout=5)
            
            if response.status_code == 200:
                flash('Magasin modifié avec succès!', 'success')
            else:
                flash('Erreur lors de la modification du magasin', 'error')
                
        except Exception as e:
            logger.error(f"Error updating store: {str(e)}")
            flash('Erreur lors de la modification du magasin', 'error')
        
        return redirect(url_for('stores'))
    
    # Affichage du formulaire d'édition
    try:
        response = requests.get(f"{SERVICES['store']}/stores/{store_id}", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'},
                              timeout=5)
        store_data = response.json() if response.status_code == 200 else {}
        return render_template('edit_store.html', store=store_data)
    except Exception as e:
        logger.error(f"Error loading store: {str(e)}")
        flash('Erreur lors du chargement du magasin', 'error')
        return redirect(url_for('stores'))

@app.route('/stores/<int:store_id>/delete', methods=['POST'])
@require_login
def delete_store(store_id):
    """Supprimer un magasin"""
    try:
        response = requests.delete(f"{SERVICES['store']}/stores/{store_id}", 
                                 headers={'Authorization': f'Bearer {API_TOKEN}'},
                                 timeout=5)
        
        if response.status_code == 200:
            flash('Magasin supprimé avec succès!', 'success')
        else:
            flash('Erreur lors de la suppression du magasin', 'error')
            
    except Exception as e:
        logger.error(f"Error deleting store: {str(e)}")
        flash('Erreur lors de la suppression du magasin', 'error')
    
    return redirect(url_for('stores'))

@app.route('/products', methods=['GET', 'POST'])
@responsable_produit_required
def products():
    """Liste des produits"""
    if request.method == 'POST':
        # Création d'un nouveau produit
        try:
            product_data = {
                'name': request.form.get('name'),
                'description': request.form.get('description', ''),
                'price': float(request.form.get('price', 0)),
                'category': request.form.get('category'),
                'stock': int(request.form.get('stock', 0)),
                'store_id': int(request.form.get('store_id', 1))
            }
            
            response = requests.post(f"{SERVICES['product']}/products", 
                                   json=product_data,
                                   headers={'Authorization': f'Bearer {API_TOKEN}'},
                                   timeout=5)
            
            if response.status_code == 201:
                flash('Produit créé avec succès!', 'success')
            else:
                flash('Erreur lors de la création du produit', 'error')
                
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            flash('Erreur lors de la création du produit', 'error')
        
        return redirect(url_for('products'))
    
    # Affichage de la liste des produits
    try:
        response = requests.get(f"{SERVICES['product']}/products", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'},
                              timeout=5)
        products_data = response.json() if response.status_code == 200 else []
        return render_template('products.html', products=products_data)
    except Exception as e:
        logger.error(f"Error loading products: {str(e)}")
        flash('Erreur lors du chargement des produits', 'error')
        return render_template('products.html', products=[])

@app.route('/sales')
@management_required
def sales():
    """Liste des ventes"""
    try:
        response = requests.get(f"{SERVICES['sales']}/sales", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'},
                              timeout=5)
        sales_data = response.json() if response.status_code == 200 else []
        return render_template('sales.html', sales=sales_data)
    except Exception as e:
        logger.error(f"Error loading sales: {str(e)}")
        flash('Erreur lors du chargement des ventes', 'error')
        return render_template('sales.html', sales=[])

@app.route('/inventory')
@employe_magasin_required
def inventory():
    """Inventaire"""
    try:
        response = requests.get(f"{SERVICES['inventory']}/inventory/stock", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'},
                              timeout=5)
        inventory_data = response.json() if response.status_code == 200 else []
        return render_template('inventory.html', inventory=inventory_data)
    except Exception as e:
        logger.error(f"Error loading inventory: {str(e)}")
        flash('Erreur lors du chargement de l\'inventaire', 'error')
        return render_template('inventory.html', inventory=[])

@app.route('/cart')
@require_login
def cart():
    """Panier"""
    return render_template('cart.html')

@app.route('/health-status')
def health_status():
    """Status des services"""
    services_status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=2)
            services_status[service_name] = response.status_code == 200
        except:
            services_status[service_name] = False
    
    return render_template('health_status.html', services_status=services_status)

# ========== API ROUTES ==========

@app.route('/api/health')
def api_health():
    """Health check pour l'API Gateway"""
    return jsonify({"service": "api-gateway", "status": "healthy"})

@app.route('/api/health/all')
def api_health_all():
    """Health check pour tous les services"""
    services_status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=2)
            services_status[service_name] = response.status_code == 200
        except:
            services_status[service_name] = False
    
    return jsonify(services_status)

# Routes pour les stores
@app.route('/api/stores', methods=['GET', 'POST'])
@app.route('/api/stores/<int:store_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
@management_required  # Admin ou gestionnaire pour gérer les magasins
@limiter.limit("30 per minute")
def stores_proxy(store_id=None):
    path = f"stores/{store_id}" if store_id else "stores"
    return forward_request('store', path, request.method)

# Routes pour les produits
@app.route('/api/products', methods=['GET', 'POST'])
@app.route('/api/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
@responsable_produit_required  # Responsable produit pour la gestion des produits
@limiter.limit("50 per minute")
def products_proxy(product_id=None):
    path = f"products/{product_id}" if product_id else "products"
    return forward_request('product', path, request.method)

# Routes pour les ventes
@app.route('/api/sales', methods=['GET', 'POST'])
@app.route('/api/sales/<int:sale_id>', methods=['GET', 'DELETE'])
@token_required
@management_required  # Admin ou gestionnaire pour consulter les ventes
@limiter.limit("20 per minute")
def sales_proxy(sale_id=None):
    path = f"sales/{sale_id}" if sale_id else "sales"
    return forward_request('sales', path, request.method)

# Routes pour l'inventaire
@app.route('/api/inventory/stock', methods=['GET'])
@token_required
@responsable_logistique_required  # Responsable logistique pour la gestion des stocks
@limiter.limit("50 per minute")
def inventory_stock_proxy():
    return forward_request('inventory', 'inventory/stock', 'GET')

# Routes pour les customers
@app.route('/api/customers', methods=['GET'])
@app.route('/api/customers/<int:customer_id>', methods=['GET', 'PUT'])
@token_required
@authenticated_required  # Clients peuvent voir/modifier leurs propres infos, admin/gestionnaire peuvent tout voir
@limiter.limit("30 per minute")
def customers_proxy(customer_id=None):
    path = f"api/customers/{customer_id}" if customer_id else "api/customers"
    return forward_request('customer', path, request.method)

# Routes pour le panier
@app.route('/api/cart', methods=['GET', 'POST'])
@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
@token_required
@authenticated_required  # Tous les utilisateurs connectés peuvent gérer leur panier
@limiter.limit("30 per minute")
def cart_proxy(item_id=None):
    path = f"cart/{item_id}" if item_id else "cart"
    return forward_request('cart', path, request.method)

# Routes pour le checkout
@app.route('/api/checkout', methods=['POST'])
@token_required
@authenticated_required  # Tous les utilisateurs connectés peuvent effectuer un checkout
@limiter.limit("10 per minute")
def checkout_proxy():
    return forward_request('checkout', 'checkout', 'POST')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
