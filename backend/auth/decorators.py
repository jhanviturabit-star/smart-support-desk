from functools import wraps
from flask import Flask, request, jsonify, g
from auth.jwt_utils import decode_token
import jwt, os

def require_roles(*roles):
    def decorators(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            if not auth_header:
                return jsonify({'error' : 'Token Missing'}), 401
            
            try:
                token = auth_header.split(" ")[1]
                payload = decode_token(token)

                if payload['role'] not in roles:
                    return jsonify({'error' : 'Access denied'}), 403
                
                g.user_id = payload['user_id'] #attach user information
                g.role = payload['role']

            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error' : 'Invalid token'}), 401
            
            return fn(*args, **kwargs)
        return wrapper
    return decorators