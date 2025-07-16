from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import requests
from functools import wraps

bp = Blueprint('web', __name__)

# Configuration
API_GATEWAY_URL = 'http://10.194.32.174:8080'

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'token' not in session:
            return redirect(url_for('web.login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session:
                return redirect(url_for('web.login'))
            user_role = session['user'].get('role')
            if user_role not in roles:
                flash('Accès interdit', 'error')
                return redirect(url_for('web.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Routes publiques
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = {
            'username': request.form['username'],
            'password': request.form['password']
        }
        
        try:
            response = requests.post(f'{API_GATEWAY_URL}/auth/login', json=data)
            if response.status_code == 200:
                result = response.json()
                session['token'] = result['token']
                session['user'] = result.get('user', {})
                return redirect(url_for('web.dashboard'))
            else:
                flash('Identifiants invalides', 'error')
        except Exception as e:
            flash('Erreur de connexion', 'error')
    
    return render_template('auth/login.html')

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = {
            'username': request.form['username'],
            'email': request.form['email'],
            'password': request.form['password'],
            'role': request.form['role']
        }
        
        try:
            response = requests.post(f'{API_GATEWAY_URL}/auth/register', json=data)
            if response.status_code == 201:
                flash('Inscription réussie !', 'success')
                return redirect(url_for('web.login'))
            else:
                flash('Erreur lors de l\'inscription', 'error')
        except Exception as e:
            flash('Erreur de connexion', 'error')
    
    return render_template('auth/register.html')

@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('web.login'))

# Dashboard principal
@bp.route('/dashboard')
#@login_required
def dashboard():
    user_role = session['user'].get('role')
    
    if user_role == 'client':
        return redirect(url_for('web.client_catalog'))
    elif user_role == 'employe_magasin':
        return redirect(url_for('web.employee_sales'))
    elif user_role == 'responsable_produit':
        return redirect(url_for('web.product_manager_products'))
    elif user_role == 'responsable_logistique':
        return redirect(url_for('web.logistics_logistics'))
    elif user_role == 'gestionnaire':
        return redirect(url_for('web.manager_dashboard'))
    elif user_role == 'admin':
        return redirect(url_for('web.admin_dashboard'))
    
    return redirect(url_for('web.login'))

# Routes Client
@bp.route('/client/catalog')
#@login_required
#@role_required(['client'])
def client_catalog():
    return render_template('client/catalog.html', current_user=session['user'])

@bp.route('/client/cart')
# @login_required
# @role_required(['client'])
def client_cart():
    return render_template('client/cart.html', current_user=session['user'])

@bp.route('/client/orders')
# @login_required
# @role_required(['client'])
def client_orders():
    return render_template('client/orders.html', current_user=session['user'])

# Routes Employé
@bp.route('/employee/sales')
# @login_required
# @role_required(['employe_magasin'])
def employee_sales():
    return render_template('employee/sales.html', current_user=session['user'])

@bp.route('/employee/stock')
# @login_required
# @role_required(['employe_magasin'])
def employee_stock():
    return render_template('employee/stock.html', current_user=session['user'])

# Routes Responsable Produit
@bp.route('/product_manager/products')
# @login_required
# @role_required(['responsable_produit'])
def product_manager_products():
    return render_template('product_manager/products.html', current_user=session['user'])

@bp.route('/product_manager/inventory')
# @login_required
# @role_required(['responsable_produit'])
def product_manager_inventory():
    return render_template('product_manager/inventory.html', current_user=session['user'])

# Routes Logistique
@bp.route('/logistics/logistics')
# @login_required
# @role_required(['responsable_logistique'])
def logistics_logistics():
    return render_template('logistics/logistics.html', current_user=session['user'])

@bp.route('/logistics/reports')
# @login_required
# @role_required(['responsable_logistique'])
def logistics_reports():
    return render_template('logistics/reports.html', current_user=session['user'])

# Routes Gestionnaire
@bp.route('/manager/dashboard')
# @login_required
# @role_required(['gestionnaire'])
def manager_dashboard():
    return render_template('manager/dashboard.html', current_user=session['user'])

@bp.route('/manager/management')
# @login_required
# @role_required(['gestionnaire'])
def manager_management():
    return render_template('manager/management.html', current_user=session['user'])

# Routes Admin
@bp.route('/admin/dashboard')
# @login_required
# @role_required(['admin'])
def admin_dashboard():
    return render_template('admin/admin_dashboard.html', current_user=session['user'])

@bp.route('/admin/user_management')
# @login_required
# @role_required(['admin'])
def admin_user_management():
    return render_template('admin/user_management.html', current_user=session['user'])