import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'web_secret_key')
    API_GATEWAY_URL = os.environ.get('API_GATEWAY_URL', 'http://10.194.32.174:8080')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret_key')