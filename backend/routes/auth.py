from flask import request, jsonify, Blueprint
#from permissions import ROLE_PERMISSIONS
from db import get_db_connection
import bcrypt
import mysql.connector
from auth.jwt_utils import generate_token

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data or "email" not in data or "password" not in data:
        return jsonify({"error": "Email and password required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT user_id, password_hash, role FROM users WHERE email=%s",
        (data["email"],)
    )
    user = cursor.fetchone()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(
        data["password"].encode(),
        user["password_hash"].encode()
    ):
        return jsonify({"error": "Invalid credentials"}), 401

    from auth.jwt_utils import generate_token
    token = generate_token(user["user_id"], user["role"])

    return jsonify({
        "token": token,
        "role": user["role"]
    }), 200


# def require_permission(permission_name):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             user_role = request.headers.get("X-User-Role")
#             if not user_role:
#                 return jsonify({"error": "User role missing"}), 401

#             user_role = user_role.upper()
#             allowed_permissions = ROLE_PERMISSIONS.get(user_role)

#             if not allowed_permissions:
#                 return jsonify({"error": "Invalid role"}), 403

#             if permission_name not in allowed_permissions:
#                 return jsonify({"error": "Permission denied"}), 403

#             return func(*args, **kwargs)
#         wrapper.__name__ = func.__name__
#         return wrapper
#     return decorator

