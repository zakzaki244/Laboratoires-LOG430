// Configuration API
const API_BASE_URL = window.location.origin;

// Fonctions utilitaires pour les appels API
class ApiService {
    static async request(endpoint, options = {}) {
        const token = localStorage.getItem('token');
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` })
            }
        };

        const config = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Erreur de requête');
            }
            
            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Auth
    static async login(credentials) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify(credentials)
        });
    }

    static async register(userData) {
        return this.request('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }

    // Users
    static async getUsers() {
        return this.request('/users');
    }

    static async getUser(userId) {
        return this.request(`/users/${userId}`);
    }

    static async updateUser(userId, userData) {
        return this.request(`/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(userData)
        });
    }

    static async deleteUser(userId) {
        return this.request(`/users/${userId}`, {
            method: 'DELETE'
        });
    }

    // Products
    static async getProducts(storeId = null) {
        const params = storeId ? `?store_id=${storeId}` : '';
        return this.request(`/products${params}`);
    }

    static async getProduct(productId) {
        return this.request(`/products/${productId}`);
    }

    static async createProduct(productData) {
        return this.request('/products', {
            method: 'POST',
            body: JSON.stringify(productData)
        });
    }

    static async updateProduct(productId, productData) {
        return this.request(`/products/${productId}`, {
            method: 'PUT',
            body: JSON.stringify(productData)
        });
    }

    static async deleteProduct(productId) {
        return this.request(`/products/${productId}`, {
            method: 'DELETE'
        });
    }

    static async updateStock(productId, quantity) {
        return this.request(`/products/${productId}/stock`, {
            method: 'PATCH',
            body: JSON.stringify({ quantity_stock: quantity })
        });
    }

    // Stores
    static async getStores() {
        return this.request('/stores');
    }

    static async getStore(storeId) {
        return this.request(`/stores/${storeId}`);
    }

    static async createStore(storeData) {
        return this.request('/stores', {
            method: 'POST',
            body: JSON.stringify(storeData)
        });
    }

    static async updateStore(storeId, storeData) {
        return this.request(`/stores/${storeId}`, {
            method: 'PUT',
            body: JSON.stringify(storeData)
        });
    }

    static async deleteStore(storeId) {
        return this.request(`/stores/${storeId}`, {
            method: 'DELETE'
        });
    }

    // Sales
    static async getSales() {
        return this.request('/sales');
    }

    static async getSale(saleId) {
        return this.request(`/sales/${saleId}`);
    }

    static async createSale(saleData) {
        return this.request('/sales', {
            method: 'POST',
            body: JSON.stringify(saleData)
        });
    }

    static async deleteSale(saleId) {
        return this.request(`/sales/${saleId}`, {
            method: 'DELETE'
        });
    }

    static async getSalesReport(startDate = null, endDate = null) {
        const params = new URLSearchParams();
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        return this.request(`/sales/report?${params.toString()}`);
    }

    // Cart
    static async getCart(storeId) {
        return this.request(`/cart?store_id=${storeId}`);
    }

    static async addToCart(itemData) {
        return this.request('/cart/items', {
            method: 'POST',
            body: JSON.stringify(itemData)
        });
    }

    static async updateCartItem(productId, quantity, storeId) {
        return this.request(`/cart/items/${productId}`, {
            method: 'PUT',
            body: JSON.stringify({ quantity, store_id: storeId })
        });
    }

    static async removeFromCart(productId, storeId) {
        return this.request(`/cart/items/${productId}?store_id=${storeId}`, {
            method: 'DELETE'
        });
    }

    static async clearCart(storeId) {
        return this.request(`/cart?store_id=${storeId}`, {
            method: 'DELETE'
        });
    }

    // Checkout
    static async processCheckout(checkoutData) {
        return this.request('/checkout', {
            method: 'POST',
            body: JSON.stringify(checkoutData)
        });
    }

    static async getCheckout(checkoutId) {
        return this.request(`/checkout/${checkoutId}`);
    }

    static async getCheckoutHistory() {
        return this.request('/checkout/history');
    }
}

// Utilitaires
class Utils {
    static showAlert(message, type = 'info') {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type}`;
        alertDiv.textContent = message;
        
        const container = document.querySelector('.main-content');
        container.insertBefore(alertDiv, container.firstChild);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }

    static formatPrice(price) {
        return new Intl.NumberFormat('fr-FR', {
            style: 'currency',
            currency: 'EUR'
        }).format(price);
    }

    static formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('fr-FR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    static showLoading(element) {
        element.innerHTML = '<span class="loading"></span> Chargement...';
    }

    static hideLoading(element, originalContent) {
        element.innerHTML = originalContent;
    }
}

// Gestion de l'authentification
class AuthManager {
    static isAuthenticated() {
        return localStorage.getItem('token') !== null;
    }

    static getCurrentUser() {
        const userStr = localStorage.getItem('user');
        return userStr ? JSON.parse(userStr) : null;
    }

    static logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
    }

    static hasRole(role) {
        const user = this.getCurrentUser();
        return user && user.role === role;
    }

    static hasAnyRole(roles) {
        const user = this.getCurrentUser();
        return user && roles.includes(user.role);
    }
}