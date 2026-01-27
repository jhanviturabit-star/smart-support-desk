from flask import jsonify, request, Blueprint
from pydantic import ValidationError
from db import get_db_connection
from models.customer import CreateCustomer
from auth.decorators import require_roles
import mysql.connector

customers_bp = Blueprint('customers', __name__)

@customers_bp.route("/create", methods=["POST"])
@require_roles('AGENT', 'TEAM_LEAD')
def create_customer():

    try:
        data = CreateCustomer(**request.json)
    except ValidationError as e:
        return jsonify({
            "error": "Invalid input",
            "details": e.errors()
        }), 400


    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO customers (c_name, c_email, phone)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (data.c_name, data.c_email, data.phone))
        conn.commit()

        return jsonify({
            "message": "Customer created successfully",
            "customer_id": cursor.lastrowid
        }), 201

    except mysql.connector.Error as e:
        return jsonify({
            "error": "Database error",
            "details": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close()


@customers_bp.route('/', methods=['GET'])
@require_roles('AGENT', 'TEAM_LEAD')
def get_customers():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT * from customers
        """
        cursor.execute(query)
        
        customers = cursor.fetchall()

        return jsonify(customers), 200

    except mysql.connector.Error as e:
        return jsonify({
            "error" : "No customers found!",
            "details" : str(e)
        }), 500
    
    finally:
        cursor.close()
        conn.close()

