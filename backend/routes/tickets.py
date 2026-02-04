from models.ticket import CreateTicket
import mysql.connector, json
from flask import jsonify, Flask, request, Blueprint, g
from pydantic import ValidationError
from db import get_db_connection
from auth.decorators import require_roles

tickets_bp = Blueprint('tickets', __name__)

@tickets_bp.route("/create", methods=["POST"])
@require_roles('AGENT', 'TEAM_LEAD')
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
            INSERT INTO tickets (c_id, t_title, t_description, priority, t_status, created_by, assigned_agent_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (data.c_id, data.t_title, data.t_description, data.priority, data.t_status, g.user_id, g.user_id))
        conn.commit()

        return jsonify({
            "message": "Ticket created successfully",
            "ticket_id": cursor.lastrowid
        }), 201

    except mysql.connector.Error as e:
        return jsonify({
            "error": "Database error",
            "details": str(e)
        }), 500

    finally:
        cursor.close()
        conn.close() 

@tickets_bp.route('/', methods=['GET'])
@require_roles('AGENT', 'TEAM_LEAD')
def get_tickets():
    status = request.args.get('status')
    priority = request.args.get('priority')

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        query = """
        SELECT t.t_id, t.t_title, t.t_description, t.priority, t.t_status, t.created_at, t.created_by, t.assigned_agent_id,
        c.c_id, c.c_name from tickets t JOIN customers c ON t.c_id = c.c_id WHERE 1=1
        """

        params = []

        if status:
            query += " ADD t.t_status = %s"
            params.append(status)

        if priority:
            query += " ADD t.priority = %s"
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

#Ticket updates by admins & agents
@tickets_bp.route("/<int:ticket_id>", methods=["PATCH"])
@require_roles('AGENT', 'TEAM_LEAD', 'ADMIN')
def update_ticket(ticket_id):
    data = request.json
    status = data.get("t_status")
    priority = data.get("priority")

    if not status and not priority:
        return jsonify({"error": "Nothing to update"}), 400

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        #1. Get the ticket info
        cursor.execute("SELECT * FROM tickets WHERE t_id=%s", (ticket_id,))
        ticket = cursor.fetchone()

        if not ticket:
            return jsonify({"error": "Ticket not found"}), 404

        # Authorization: AGENT can only update their own tickets
        user_role = data.get('role')
        user_id = data.get('user_id')
        # print('-----------------------------------------------------------')
        # print(user_role)
        if user_role == "AGENT" and ticket.get("assigned_agent_id") != user_id:
            return jsonify({"error": "Permission denied"}), 403

        # Build dynamic query
        fields = []
        params = []

        if status:
            fields.append("t_status=%s")
            params.append(status)

        if priority:
            fields.append("priority=%s")
            params.append(priority)

        params.append(ticket_id)

        query = f"UPDATE tickets SET {', '.join(fields)} WHERE t_id=%s"
        cursor.execute(query, params)
        conn.commit()

        return jsonify({"message": "Ticket updated successfully"}), 200

    except mysql.connector.Error as e:
        return jsonify({"error": "Database error", "details": str(e)}), 500

    finally:
        cursor.close()
        conn.close()

#Delete ticket by admins & agents
@tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
@require_roles('AGENT', 'ADMIN')
def delete_ticket(ticket_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    #Fetch tickets
    cursor.execute('SELECT t_id, created_by FROM tickets WHERE t_id = %s', (ticket_id,))

    ticket = cursor.fetchone()

    if not ticket:
        cursor.close()
        conn.close()
        return jsonify({'error' : 'Ticket not found'}), 404
    
    #Permission check
    if g.role != 'ADMIN' and ticket['created_by'] != g.user_id:
        cursor.close()
        conn.close()
        return jsonify({'error': 'Access denied'}), 403
    
    #Delete ticket
    cursor.execute(
        'DELETE FROM tickets WHERE t_id = %s',
        (ticket_id,)
    )
    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({'message': 'Ticket deleted successfully'}), 200
    

