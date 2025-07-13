from flask import Flask, request, jsonify, render_template, redirect, url_for, session, flash
import requests
import os
from functools import wraps
from prometheus_flask_exporter import PrometheusMetrics
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logging

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')
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
        print(f"DEBUG: Forwarding {method} request to {url}")
        
        # Transférer les headers d'authentification
        headers = {}
        if 'Authorization' in request.headers:
            headers['Authorization'] = request.headers['Authorization']
        
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=request.args)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=request.json)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, json=request.json)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        
        print(f"DEBUG: Response from {service_name}: {response.status_code}")
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Request error: {e}")
        logging.error(f"Erreur lors de la communication avec {service_name}: {e}")
        return {"error": "Service indisponible"}, 503
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        return {"error": "Service indisponible"}, 503

# Routes pour les magasins
@app.route('/api/stores', methods=['GET'])
@app.route('/api/stores/<int:store_id>', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def stores_proxy(store_id=None):
    path = f"stores/{store_id}" if store_id else "stores"
    return forward_request('store', path, request.method)

# Routes pour les produits
@app.route('/api/products', methods=['GET', 'POST'])
@app.route('/api/products/<int:product_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
@limiter.limit("50 per minute")
def products_proxy(product_id=None):
    path = f"products/{product_id}" if product_id else "products"
    return forward_request('product', path, request.method)

@app.route('/api/products/search', methods=['GET'])
@token_required
@limiter.limit("100 per minute")
def product_search_proxy():
    return forward_request('product', 'products/search', 'GET')

# Routes pour les ventes
@app.route('/api/sales', methods=['GET', 'POST'])
@app.route('/api/sales/<int:sale_id>', methods=['GET', 'DELETE'])
@token_required
@limiter.limit("20 per minute")
def sales_proxy(sale_id=None):
    path = f"sales/{sale_id}" if sale_id else "sales"
    return forward_request('sales', path, request.method)

@app.route('/api/sales/<int:sale_id>/refund', methods=['POST'])
@token_required
@limiter.limit("10 per minute")
def refund_proxy(sale_id):
    return forward_request('sales', f'sales/{sale_id}/refund', 'POST')

# Routes pour l'inventaire
@app.route('/api/inventory/restock', methods=['GET', 'POST'])
@token_required
@limiter.limit("20 per minute")
def inventory_proxy():
    return forward_request('inventory', 'inventory/restock', request.method)

@app.route('/api/inventory/stock', methods=['GET'])
@token_required
@limiter.limit("50 per minute")
def stock_proxy():
    return forward_request('inventory', 'inventory/stock', 'GET')

# Routes pour les clients
@app.route('/api/customers/register', methods=['POST'])
@limiter.limit("5 per minute")
def customer_register_proxy():
    return forward_request('customer', 'api/customers/register', 'POST')

@app.route('/api/customers/login', methods=['POST'])
@limiter.limit("10 per minute")
def customer_login_proxy():
    return forward_request('customer', 'api/customers/login', 'POST')

@app.route('/api/customers', methods=['GET'])
@app.route('/api/customers/<int:customer_id>', methods=['GET', 'PUT'])
@token_required
@limiter.limit("30 per minute")
def customers_proxy(customer_id=None):
    path = f"api/customers/{customer_id}" if customer_id else "api/customers"
    return forward_request('customer', path, request.method)

@app.route('/api/customers/<int:customer_id>/change-password', methods=['POST'])
@token_required
@limiter.limit("3 per minute")
def change_password_proxy(customer_id):
    return forward_request('customer', f'api/customers/{customer_id}/change-password', 'POST')

@app.route('/api/customers/search', methods=['GET'])
@token_required
@limiter.limit("20 per minute")
def customer_search_proxy():
    return forward_request('customer', 'api/customers/search', 'GET')

# Routes pour le panier
@app.route('/api/cart/<int:customer_id>', methods=['GET'])
@token_required
@limiter.limit("50 per minute")
def cart_proxy(customer_id):
    return forward_request('cart', f'cart/{customer_id}', 'GET')

@app.route('/api/cart/<int:customer_id>/items', methods=['POST'])
@token_required
@limiter.limit("30 per minute")
def add_to_cart_proxy(customer_id):
    return forward_request('cart', f'cart/{customer_id}/items', 'POST')

@app.route('/api/cart/<int:customer_id>/items/<int:product_id>', methods=['PUT', 'DELETE'])
@token_required
@limiter.limit("20 per minute")
def cart_item_proxy(customer_id, product_id):
    return forward_request('cart', f'cart/{customer_id}/items/{product_id}', request.method)

@app.route('/api/cart/<int:customer_id>/clear', methods=['DELETE'])
@token_required
@limiter.limit("10 per minute")
def clear_cart_proxy(customer_id):
    return forward_request('cart', f'cart/{customer_id}/clear', 'DELETE')

@app.route('/api/cart/<int:customer_id>/summary', methods=['GET'])
@token_required
@limiter.limit("30 per minute")
def cart_summary_proxy(customer_id):
    return forward_request('cart', f'cart/{customer_id}/summary', 'GET')

# Routes pour le checkout
@app.route('/api/checkout/preview/<int:customer_id>', methods=['POST'])
@token_required
@limiter.limit("10 per minute")
def checkout_preview_proxy(customer_id):
    return forward_request('checkout', f'checkout/preview/{customer_id}', 'POST')

@app.route('/api/checkout/process/<int:customer_id>', methods=['POST'])
@token_required
@limiter.limit("5 per minute")
def checkout_process_proxy(customer_id):
    return forward_request('checkout', f'checkout/process/{customer_id}', 'POST')

@app.route('/api/orders/<int:customer_id>', methods=['GET'])
@token_required
@limiter.limit("20 per minute")
def orders_proxy(customer_id):
    return forward_request('checkout', f'orders/{customer_id}', 'GET')

@app.route('/api/orders/<int:order_id>', methods=['GET'])
@token_required
@limiter.limit("20 per minute")
def order_details_proxy(order_id):
    return forward_request('checkout', f'orders/{order_id}', 'GET')

@app.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
@token_required
@limiter.limit("5 per minute")
def cancel_order_proxy(order_id):
    return forward_request('checkout', f'orders/{order_id}/cancel', 'POST')

@app.route('/api/orders/stats', methods=['GET'])
@token_required
@limiter.limit("10 per minute")
def order_stats_proxy():
    return forward_request('checkout', 'orders/stats', 'GET')

# Route d'information etat du systeme 
@app.route('/health')
def health_check():
    return {"status": "healthy", "services": SERVICES}

# Routes Web pour l'interface utilisateur
@app.route('/')
def index():
    """Page d'accueil avec dashboard"""
    # Vérifier si l'utilisateur est connecté
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Récupérer les informations du dashboard
    try:
        # Récupérer les magasins
        stores_response = requests.get(f"{SERVICES['store']}/stores")
        stores = stores_response.json() if stores_response.status_code == 200 else []
        
        # Récupérer les statistiques
        stats_response = requests.get(f"{SERVICES['checkout']}/orders/stats", 
                                      headers={'Authorization': f'Bearer {API_TOKEN}'})
        stats = stats_response.json() if stats_response.status_code == 200 else {}
        
        # Récupérer les produits les plus vendus
        products_response = requests.get(f"{SERVICES['product']}/products", 
                                       headers={'Authorization': f'Bearer {API_TOKEN}'})
        products = products_response.json() if products_response.status_code == 200 else []
        
        return render_template('index.html', 
                             stores=stores, 
                             stats=stats, 
                             products=products[:5])  # Top 5 produits
    except Exception as e:
        flash(f"Erreur lors du chargement du dashboard: {str(e)}", "error")
        return render_template('index.html', stores=[], stats={}, products=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Page de connexion"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            # Convertir username en email pour l'API customer-service
            if username == 'admin':
                email = 'admin@test.com'
                # Essayer d'abord avec admin123, puis avec admin
                passwords = ['admin123', 'admin']
            else:
                email = f"{username}@test.com" if '@' not in username else username
                passwords = [password]
            
            success = False
            for pwd in passwords:
                url = f"{SERVICES['customer']}/api/customers/login"
                print(f"DEBUG: Attempting login with URL: {url}")
                response = requests.post(url, json={'email': email, 'password': pwd})
                print(f"DEBUG: Response status: {response.status_code}")
                
                if response.status_code == 200:
                    user_data = response.json()
                    customer_data = user_data.get('customer', {})
                    session['user_id'] = customer_data.get('id')
                    session['username'] = username
                    session['email'] = customer_data.get('email')
                    session['role'] = 'admin' if username == 'admin' else 'customer'
                    flash("Connexion réussie!", "success")
                    success = True
                    break
            
            if success:
                return redirect(url_for('index'))
            else:
                flash("Nom d'utilisateur ou mot de passe incorrect", "error")
        except Exception as e:
            flash(f"Erreur de connexion: {str(e)}", "error")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Déconnexion"""
    session.clear()
    flash("Déconnexion réussie!", "success")
    return redirect(url_for('login'))

@app.route('/stores')
def stores():
    """Liste des magasins"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        response = requests.get(f"{SERVICES['store']}/stores")
        stores_data = response.json() if response.status_code == 200 else []
        return render_template('stores.html', stores=stores_data)
    except Exception as e:
        flash(f"Erreur lors du chargement des magasins: {str(e)}", "error")
        return render_template('stores.html', stores=[])

@app.route('/products')
def products():
    """Liste des produits"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        response = requests.get(f"{SERVICES['product']}/products", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'})
        products_data = response.json() if response.status_code == 200 else []
        return render_template('products.html', products=products_data)
    except Exception as e:
        flash(f"Erreur lors du chargement des produits: {str(e)}", "error")
        return render_template('products.html', products=[])

@app.route('/inventory')
def inventory():
    """Gestion des stocks"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        response = requests.get(f"{SERVICES['inventory']}/inventory/stock", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'})
        inventory_data = response.json() if response.status_code == 200 else []
        return render_template('inventory.html', inventory=inventory_data)
    except Exception as e:
        flash(f"Erreur lors du chargement du stock: {str(e)}", "error")
        return render_template('inventory.html', inventory=[])

@app.route('/sales')
def sales():
    """Historique des ventes"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        response = requests.get(f"{SERVICES['sales']}/sales", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'})
        sales_data = response.json() if response.status_code == 200 else []
        return render_template('sales.html', sales=sales_data)
    except Exception as e:
        flash(f"Erreur lors du chargement des ventes: {str(e)}", "error")
        return render_template('sales.html', sales=[])

@app.route('/cart')
def cart():
    """Panier de l'utilisateur"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        customer_id = session['user_id']
        response = requests.get(f"{SERVICES['cart']}/cart/{customer_id}", 
                              headers={'Authorization': f'Bearer {API_TOKEN}'})
        cart_data = response.json() if response.status_code == 200 else {}
        return render_template('cart.html', cart=cart_data)
    except Exception as e:
        flash(f"Erreur lors du chargement du panier: {str(e)}", "error")
        return render_template('cart.html', cart={})

@app.route('/health-status')
def health_status():
    """Page de statut des services"""
    services_status = {}
    
    for service_name, service_url in SERVICES.items():
        try:
            response = requests.get(f"{service_url}/health", timeout=5)
            services_status[service_name] = {
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'response_time': response.elapsed.total_seconds(),
                'url': service_url
            }
        except Exception as e:
            services_status[service_name] = {
                'status': 'error',
                'error': str(e),
                'url': service_url
            }
    
    return render_template('health_status.html', services=services_status)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
