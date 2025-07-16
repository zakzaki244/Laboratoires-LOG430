import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'web_secret_key')
    API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL', 'http://api-gateway:8080')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_key')