import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret')
    
    # URLs des microservices
    CUSTOMER_SERVICE_URL = os.environ.get('CUSTOMER_SERVICE_URL', 'http://customer-service:5000')
    PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:5000')
    SALES_SERVICE_URL = os.environ.get('SALES_SERVICE_URL', 'http://sales-service:5000')
    STORE_SERVICE_URL = os.environ.get('STORE_SERVICE_URL', 'http://store-service:5000')
    CART_SERVICE_URL = os.environ.get('CART_SERVICE_URL', 'http://cart-service:5000')
    CHECKOUT_SERVICE_URL = os.environ.get('CHECKOUT_SERVICE_URL', 'http://checkout-service:5000')