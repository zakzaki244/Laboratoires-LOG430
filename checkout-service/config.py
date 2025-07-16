import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://log430:laboratoire@10.194.32.174:5432/checkoutdb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret')
    
    # URLs des autres microservices
    CART_SERVICE_URL = os.environ.get('CART_SERVICE_URL', 'http://cart-service:5000')
    SALES_SERVICE_URL = os.environ.get('SALES_SERVICE_URL', 'http://sales-service:5000')
    PRODUCT_SERVICE_URL = os.environ.get('PRODUCT_SERVICE_URL', 'http://product-service:5000')