import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://log430:laboratoire@10.194.32.174:5432/productdb')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt_secret')