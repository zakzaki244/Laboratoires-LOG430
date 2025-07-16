import jwt
from flask import request, current_app, g
from functools import wraps

def decode_jwt(token):
    return jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])

def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get('Authorization', None)
        if not auth or not auth.startswith('Bearer '):
            return {'message': 'Token manquant ou invalide'}, 401
        token = auth.split(' ')[1]
        try:
            payload = decode_jwt(token)
            g.user = payload
        except Exception:
            return {'message': 'Token invalide'}, 401
        return f(*args, **kwargs)
    return decorated

def role_required(roles):
    def role_decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            user = getattr(g, 'user', None)
            if not user or user.get('role') not in roles:
                return {'message': 'Accès interdit'}, 403
            return f(*args, **kwargs)
        return decorated
    return role_decorator