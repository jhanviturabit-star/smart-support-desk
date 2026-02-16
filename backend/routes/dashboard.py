import json
from flask import jsonify, Flask, request, Blueprint, g
from db import get_db_connection
from redis_client import redis_client
from auth.decorators import require_roles

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@require_roles('ADMIN', 'AGENT')
def dashboard_summary():

    user_id = int(g.user_id)
    is_admin = (g.role == "ADMIN")
    
    cache_key = f"dashboard:{g.role}:{user_id}"

    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        #base condition
        where_clause = ""
        params = []

        if not is_admin:
            where_clause = "WHERE assigned_agent_id = %s" 
            params.append(user_id)

        #total tickets
        cursor.execute(
            f"SELECT COUNT(*) AS total FROM tickets {where_clause}",
            params
        )
        total = cursor.fetchone()["total"]

        #tickets by status (user specific)
        cursor.execute(
            f"""
            SELECT t_status, COUNT(*) AS count
            FROM tickets
            {where_clause}
            GROUP BY t_status
            """,
            params
        )
        status_counts = cursor.fetchall()

        #tickets by priority (user specific)
        cursor.execute(
            f"""
            SELECT priority, COUNT(*) AS count
            FROM tickets
            {where_clause}
            GROUP BY priority
            """,
            params
        )
        priority_counts = cursor.fetchall()

        #Top N customers by ticket
        customer_where = ""
        customer_params = []

        if not is_admin:
            customer_where = "WHERE t.assigned_agent_id = %s"
            customer_params.append(user_id)

        cursor.execute(
            f"""
            SELECT c.c_name, COUNT(t.t_id) AS ticket_count
            FROM tickets t
            JOIN customers c ON t.c_id = c.c_id
            {customer_where}
            GROUP BY c.c_id, c.c_name
            ORDER BY ticket_count DESC
            LIMIT 5
            """,
            customer_params
        )
        top_customers = cursor.fetchall()

        result = {
            'total_tickets': total,
            'tickets_by_status' : status_counts,
            'tickets_by_priority' : priority_counts,
            'top_customers' : top_customers
        }

        redis_client.setex(cache_key, 60, json.dumps(result))

        return jsonify({
            'source' : 'database',
            'data' : result
        }), 200
    
    except Exception as e:
        return jsonify({
            'error' : 'database error',
            'details' : str(e)
        }), 500
    
    finally:
        cursor.close()
        conn.close()