from functools import wraps
from flask import Flask, request, jsonify, g
from auth.jwt_utils import decode_token
import jwt, os

def require_roles(*roles):
    def decorators(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')

            print("\n------ AUTH DEBUG ------")
            print("Authorization header received:", auth_header)
            print("------------------------\n")

            if not auth_header:
                return jsonify({'error' : 'Token Missing'}), 401
            
            try:
                token = auth_header.split(" ")[1]
                payload = decode_token(token)

                if payload['role'] not in roles:
                    return jsonify({'error' : 'Access denied'}), 403    
                
                g.user_id = payload['user_id'] #attach user information
                g.role = payload['role']

                # Debugging user_id and role
                print(f"User ID from token: {g.user_id}")  # Print user_id to check if it's set correctly
                print(f"User role from token: {g.role}")  # Print role to confirm it's correct

            except jwt.ExpiredSignatureError:
                return jsonify({'error': 'Token expired'}), 401
            except jwt.InvalidTokenError:
                return jsonify({'error' : 'Invalid token'}), 401
            
            return fn(*args, **kwargs)
        return wrapper
    return decorators