from flask import jsonify, Flask, request, Blueprint
from pydantic import ValidationError
from db import get_db_connection
from models.user import CreateUser
import mysql.connector
import bcrypt

users_bp = Blueprint('users', __name__)

@users_bp.route("/", methods=["POST"])
def create_user():
    """
    Create a new user (Admin only - permission will be added later)
    """

    try:
        data = CreateUser(**request.json)
    except ValidationError as e:
        return jsonify({
            "error": "Invalid input",
            "details": e.errors()
        }), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # hash password
        hashed_password = bcrypt.hashpw(
            data.password.encode("utf-8"),
            bcrypt.gensalt()
        ).decode("utf-8")

        query = """
            INSERT INTO users (username, email, password, role)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (
            data.username,
            data.email,
            hashed_password,
            data.role
        ))
        conn.commit()

        return jsonify({
            "message": "User created successfully",
            "user_id": cursor.lastrowid
        }), 201

    except mysql.connector.Error as e:
        return jsonify({
            "error": "Database error",
            "details": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


@users_bp.route("/", methods=["GET"])
def get_users():
    """
    List all users (Team Lead / Admin)
    """

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT user_id, username, email, role, created_at
            FROM users
        """)
        users = cursor.fetchall()

        return jsonify(users), 200

    except mysql.connector.Error as e:
        return jsonify({
            "error": "Database error",
            "details": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()