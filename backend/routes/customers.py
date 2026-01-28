from flask import jsonify, request, Blueprint
from pydantic import ValidationError
from db import get_db_connection
from models.customer import CreateCustomer
from auth.decorators import require_roles
import mysql.connector

customers_bp = Blueprint('customers', __name__)

@customers_bp.route("/create", methods=["POST"])
@require_roles('AGENT', 'ADMIN')
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
@require_roles('AGENT', 'ADMIN')
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

@customers_bp.route('/<int:customer_id>', methods=['PUT'])
@require_roles('ADMIN')
def update_customer(customer_id): 
    # import pdb
    # pdb.set_trace()
    data = request.json or {}

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    if not name or not email:
        return jsonify({'erorr' : 'Field names are required!'}), 400
    
    if '@' not in email:
        return jsonify({'error' : 'Invalid email ID'}), 400
    
    if len(phone) > 10:
        return jsonify({'error' : 'Phone no. count exceeds'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(f"SELECT c_id from customers where c_id = {customer_id}")
    customer = cursor.fetchone()

    if not customer:
        cursor.close()
        conn.close()
        return jsonify({'error' : 'Customer not found!'}), 404
    
    #update 
    cursor.execute('UPDATE customers set c_name = %s, c_email = %s, phone = %s WHERE c_id = %s', (name, email, phone, customer_id))

    conn.commit()
    conn.close()
    cursor.close()

    return jsonify({'message' : 'Customer updated successfully!'}), 200

@customers_bp.route('/<int:customer_id>', methods=['DELETE'])
#@require_roles('ADMIN')
def delete_customer(customer_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute('SELECT c_id from customers WHERE c_id = %s', (customer_id,))
    customer = cursor.fetchone()

    if not customer:
        cursor.close()
        conn.close()
        return jsonify({'error' : 'Customer not found!'}), 404
    
    #check if customers has tickets
    cursor.execute('SELECT t_id FROM tickets WHERE c_id = %s LIMIT 1', (customer_id,))
    ticket = cursor.fetchone()

    if ticket:
        cursor.close()
        conn.close()
        return jsonify({'error' : 'Cannot delete customer with existing tickets'}), 404
    
    #delete
    cursor.execute(f'DELETE from customers WHERE c_id = {customer_id}')

    conn.commit()
    conn.close()
    cursor.close()

    return jsonify({'message' : 'Customer deleted successfully'})