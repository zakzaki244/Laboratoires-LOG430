// Initialisation de l'application
document.addEventListener('DOMContentLoaded', function() {
    // Vérifier l'authentification
    if (!AuthManager.isAuthenticated() && window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
        return;
    }

    // Initialiser les événements globaux
    initializeGlobalEvents();
    
    // Initialiser les événements spécifiques à la page
    initializePageEvents();
});

function initializeGlobalEvents() {
    // Gestion du logout
    const logoutBtn = document.querySelector('.logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            AuthManager.logout();
        });
    }

    // Gestion des formulaires avec validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
    });
}

function initializePageEvents() {
    const currentPath = window.location.pathname;
    
    // Événements spécifiques selon la page
    if (currentPath.includes('/products')) {
        initializeProductsPage();
    } else if (currentPath.includes('/cart')) {
        initializeCartPage();
    } else if (currentPath.includes('/sales')) {
        initializeSalesPage();
    } else if (currentPath.includes('/stores')) {
        initializeStoresPage();
    } else if (currentPath.includes('/admin')) {
        initializeAdminPage();
    }
}

async function handleFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;
    
    try {
        // Afficher le loading
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="loading"></span> Envoi...';
        
        // Récupérer les données du formulaire
        const formData = new FormData(form);
        const data = Object.fromEntries(formData.entries());
        
        // Appeler l'API appropriée selon le formulaire
        const action = form.dataset.action;
        let result;
        
        switch (action) {
            case 'login':
                result = await ApiService.login(data);
                handleLoginSuccess(result);
                break;
            case 'register':
                result = await ApiService.register(data);
                handleRegisterSuccess(result);
                break;
            case 'create-product':
                result = await ApiService.createProduct(data);
                handleProductCreated(result);
                break;
            case 'update-product':
                const productId = form.dataset.productId;
                result = await ApiService.updateProduct(productId, data);
                handleProductUpdated(result);
                break;
            case 'create-store':
                result = await ApiService.createStore(data);
                handleStoreCreated(result);
                break;
            case 'create-sale':
                result = await ApiService.createSale(data);
                handleSaleCreated(result);
                break;
            default:
                throw new Error('Action non reconnue');
        }
        
    } catch (error) {
        Utils.showAlert(error.message, 'error');
    } finally {
        // Restaurer le bouton
        submitBtn.disabled = false;
        submitBtn.textContent = originalText;
    }
}

// Gestionnaires de succès
function handleLoginSuccess(result) {
    localStorage.setItem('token', result.token);
    localStorage.setItem('user', JSON.stringify(result.user));
    
    // Rediriger selon le rôle
    const user = result.user;
    let redirectPath = '/dashboard';
    
    if (user.role === 'client') {
        redirectPath = '/client/catalog';
    } else if (user.role === 'employe_magasin') {
        redirectPath = '/employee/sales';
    } else if (user.role === 'responsable_produit') {
        redirectPath = '/product_manager/products';
    } else if (user.role === 'responsable_logistique') {
        redirectPath = '/logistics/logistics';
    } else if (user.role === 'gestionnaire') {
        redirectPath = '/manager/dashboard';
    } else if (user.role === 'admin') {
        redirectPath = '/admin/dashboard';
    }
    
    window.location.href = redirectPath;
}

function handleRegisterSuccess(result) {
    Utils.showAlert('Inscription réussie ! Vous pouvez maintenant vous connecter.', 'success');
    setTimeout(() => {
        window.location.href = '/login';
    }, 2000);
}

function handleProductCreated(result) {
    Utils.showAlert('Produit créé avec succès !', 'success');
    setTimeout(() => {
        window.location.reload();
    }, 1500);
}

function handleProductUpdated(result) {
    Utils.showAlert('Produit mis à jour avec succès !', 'success');
    setTimeout(() => {
        window.location.reload();
    }, 1500);
}

function handleStoreCreated(result) {
    Utils.showAlert('Magasin créé avec succès !', 'success');
    setTimeout(() => {
        window.location.reload();
    }, 1500);
}

function handleSaleCreated(result) {
    Utils.showAlert('Vente créée avec succès !', 'success');
    setTimeout(() => {
        window.location.reload();
    }, 1500);
}

// Initialisation des pages spécifiques
function initializeProductsPage() {
    loadProducts();
    
    // Événements pour les actions sur les produits
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn-edit-product')) {
            const productId = e.target.dataset.productId;
            editProduct(productId);
        } else if (e.target.matches('.btn-delete-product')) {
            const productId = e.target.dataset.productId;
            deleteProduct(productId);
        } else if (e.target.matches('.btn-update-stock')) {
            const productId = e.target.dataset.productId;
            updateStock(productId);
        }
    });
}

function initializeCartPage() {
    loadCart();
    
    // Événements pour le panier
    document.addEventListener('click', function(e) {
        if (e.target.matches('.btn-update-quantity')) {
            const productId = e.target.dataset.productId;
            const quantity = prompt('Nouvelle quantité :');
            if (quantity !== null) {
                updateCartItemQuantity(productId, parseInt(quantity));
            }
        } else if (e.target.matches('.btn-remove-item')) {
            const productId = e.target.dataset.productId;
            removeFromCart(productId);
        } else if (e.target.matches('.btn-checkout')) {
            processCheckout();
        }
    });
}

function initializeSalesPage() {
    loadSales();
    loadSalesReport();
}

function initializeStoresPage() {
    loadStores();
}

function initializeAdminPage() {
    loadUsers();
    loadSystemStats();
}

// Fonctions de chargement des données
async function loadProducts() {
    try {
        const products = await ApiService.getProducts();
        displayProducts(products);
    } catch (error) {
        Utils.showAlert('Erreur lors du chargement des produits', 'error');
    }
}

async function loadCart() {
    try {
        const storeId = getCurrentStoreId();
        const cart = await ApiService.getCart(storeId);
        displayCart(cart);
    } catch (error) {
        Utils.showAlert('Erreur lors du chargement du panier', 'error');
    }
}

async function loadSales() {
    try {
        const sales = await ApiService.getSales();
        displaySales(sales);
    } catch (error) {
        Utils.showAlert('Erreur lors du chargement des ventes', 'error');
    }
}

async function loadStores() {
    try {
        const stores = await ApiService.getStores();
        displayStores(stores);
    } catch (error) {
        Utils.showAlert('Erreur lors du chargement des magasins', 'error');
    }
}

async function loadUsers() {
    try {
        const users = await ApiService.getUsers();
        displayUsers(users);
    } catch (error) {
        Utils.showAlert('Erreur lors du chargement des utilisateurs', 'error');
    }
}

// Fonctions d'affichage
function displayProducts(products) {
    const container = document.querySelector('#products-container');
    if (!container) return;
    
    const html = products.map(product => `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">${product.name}</h3>
                <span class="badge">${product.category}</span>
            </div>
            <p>${product.description || 'Aucune description'}</p>
            <div class="product-details">
                <p><strong>Prix :</strong> ${Utils.formatPrice(product.price)}</p>
                <p><strong>Stock :</strong> ${product.quantity_stock}</p>
                <p><strong>Magasin :</strong> ${product.store_id}</p>
            </div>
            <div class="card-actions">
                <button class="btn btn-primary btn-edit-product" data-product-id="${product.id}">Modifier</button>
                <button class="btn btn-danger btn-delete-product" data-product-id="${product.id}">Supprimer</button>
                <button class="btn btn-secondary btn-update-stock" data-product-id="${product.id}">Stock</button>
            </div>
        </div>
    `).join('');
    
    container.innerHTML = html;
}

function displayCart(cart) {
    const container = document.querySelector('#cart-container');
    if (!container) return;
    
    if (!cart.items || cart.items.length === 0) {
        container.innerHTML = '<div class="alert alert-info">Votre panier est vide</div>';
        return;
    }
    
    const itemsHtml = cart.items.map(item => `
        <tr>
            <td>${item.product_id}</td>
            <td>${item.quantity}</td>
            <td>${Utils.formatPrice(item.unit_price)}</td>
            <td>${Utils.formatPrice(item.quantity * item.unit_price)}</td>
            <td>
                <button class="btn btn-primary btn-update-quantity" data-product-id="${item.product_id}">Modifier</button>
                <button class="btn btn-danger btn-remove-item" data-product-id="${item.product_id}">Supprimer</button>
            </td>
        </tr>
    `).join('');
    
    const html = `
        <div class="card">
            <div class="card-header">
                <h3 class="card-title">Panier d'achat</h3>
                <span class="total">Total: ${Utils.formatPrice(cart.total)}</span>
            </div>
            <table class="table">
                <thead>
                    <tr>
                        <th>Produit</th>
                        <th>Quantité</th>
                        <th>Prix unitaire</th>
                        <th>Sous-total</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    ${itemsHtml}
                </tbody>
            </table>
            <div class="card-actions">
                <button class="btn btn-success btn-checkout">Finaliser la commande</button>
                <button class="btn btn-danger" onclick="clearCart()">Vider le panier</button>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
}

// Fonctions utilitaires
function getCurrentStoreId() {
    // Récupérer l'ID du magasin depuis l'URL ou les paramètres
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('store_id') || 1; // Magasin par défaut
}

function editProduct(productId) {
    // Implémenter la logique d'édition
    console.log('Éditer le produit:', productId);
}

async function deleteProduct(productId) {
    if (confirm('Êtes-vous sûr de vouloir supprimer ce produit ?')) {
        try {
            await ApiService.deleteProduct(productId);
            Utils.showAlert('Produit supprimé avec succès', 'success');
            loadProducts();
        } catch (error) {
            Utils.showAlert('Erreur lors de la suppression', 'error');
        }
    }
}

async function updateStock(productId) {
    const newQuantity = prompt('Nouvelle quantité en stock :');
    if (newQuantity !== null) {
        try {
            await ApiService.updateStock(productId, parseInt(newQuantity));
            Utils.showAlert('Stock mis à jour avec succès', 'success');
            loadProducts();
        } catch (error) {
            Utils.showAlert('Erreur lors de la mise à jour du stock', 'error');
        }
    }
}

async function updateCartItemQuantity(productId, quantity) {
    try {
        const storeId = getCurrentStoreId();
        await ApiService.updateCartItem(productId, quantity, storeId);
        Utils.showAlert('Quantité mise à jour', 'success');
        loadCart();
    } catch (error) {
        Utils.showAlert('Erreur lors de la mise à jour', 'error');
    }
}

async function removeFromCart(productId) {
    try {
        const storeId = getCurrentStoreId();
        await ApiService.removeFromCart(productId, storeId);
        Utils.showAlert('Produit retiré du panier', 'success');
        loadCart();
    } catch (error) {
        Utils.showAlert('Erreur lors de la suppression', 'error');
    }
}

async function clearCart() {
    if (confirm('Êtes-vous sûr de vouloir vider le panier ?')) {
        try {
            const storeId = getCurrentStoreId();
            await ApiService.clearCart(storeId);
            Utils.showAlert('Panier vidé', 'success');
            loadCart();
        } catch (error) {
            Utils.showAlert('Erreur lors du vidage du panier', 'error');
        }
    }
}

async function processCheckout() {
    try {
        const storeId = getCurrentStoreId();
        const paymentData = {
            store_id: storeId,
            payment_data: {
                payment_method: 'card'
            }
        };
        
        const result = await ApiService.processCheckout(paymentData);
        Utils.showAlert('Commande finalisée avec succès !', 'success');
        setTimeout(() => {
            window.location.href = '/client/orders';
        }, 2000);
    } catch (error) {
        Utils.showAlert('Erreur lors de la finalisation', 'error');
    }
}