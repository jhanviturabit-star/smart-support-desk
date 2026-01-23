from flask import Flask, request, jsonify
from pydantic import ValidationError
import mysql.connector, json
from db import get_db_connection
from models.customer import CreateCustomer
from models.ticket import CreateTicket
from redis_client import redis_client

app = Flask(__name__)

@app.route("/")
def home():
    return {'message' : 'Smart Desk API is working!'}

@app.route("/customers", methods=["POST"])
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

@app.route('/customers', methods=['GET'])
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

@app.route("/tickets", methods=["POST"])
def create_ticket():

    try:
        data = CreateTicket(**request.json)
    except ValidationError as e:
        return jsonify({
            "error": "Invalid input",
            "details": e.errors()
        }), 400


    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO tickets (c_id, t_title, t_description, priority, t_status)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (data.c_id, data.t_title, data.t_description, data.priority, data.t_status))
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

@app.route('/tickets', methods=['GET'])
def get_tickets():
    status = request.args.get('status')
    priority = request.args.get('priority')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT t.t_id, t.t_title, t.t_description, t.priority, t_status, t.created_at, 
        c.c_id, c.c_name from tickets t JOIN customers c  ON t.c_id = c.c_id WHERE 1=1
        """

        params = []

        if status:
            query += " ADD t.t_status = %s"
            params.append(status)

        if priority:
            query += " ADD t.t_priority = %s"
            params.append(priority)

        cursor.execute(query, params)
        
        tickets = cursor.fetchall()

        return jsonify(tickets), 200

    except mysql.connector.Error as e:
        return jsonify({
            "error" : "No tickets generated!",
            "details" : str(e)
        }), 500
    
    finally:
        cursor.close()
        conn.close()

@app.route('/dashboard/summary', methods=['GET'])
def dashboard_summary():
    cache_key = 'dashboard_summary'

    #check into redis first
    chached_data = redis_client.get(cache_key)
    if chached_data:
        return jsonify({
            'source': 'cache',
            'data' : json.loads(chached_data)
        }), 200
    
    try: #toal tickets
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM tickets")
        total = cursor.fetchone()[total]

        #tickets by status
        cursor.execute('''SELECT t_status, COUNT(*) AS count FROM tickets GROUP BY t_status''')
        status_counts = cursor.fetchall()

        #tickets by priority
        cursor.execute('''SELECT t_priority, COUNT(*) AS count FROM tickets GROUP BY t_priority''')
        priority_counts = cursor.fetchall()

        result = {
            "total_tickets" : total,
            "tickets_by_status" : status_counts,
            "tickets_by_priority" : priority_counts
        }

        redis_client.setex(cache_key, 60, json.dumps(result))

        return jsonify({
            "source" : "database",
            "data" : result
        }), 200
    
    except Exception as e:
        return jsonify({
            'error' : 'Database Error',
            'details' : str(e)
        }), 500
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
