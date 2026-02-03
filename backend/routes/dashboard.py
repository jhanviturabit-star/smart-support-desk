import mysql.connector, json
from flask import jsonify, Flask, request, Blueprint, g
from pydantic import ValidationError
from db import get_db_connection
from redis_client import redis_client
from auth.decorators import require_roles

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@require_roles('ADMIN', 'AGENT', 'TEAM_LEAD')
def dashboard_summary():

    user_id = int(g.user_id)
    cache_key = f"dashboard:{g.role}:{user_id}"
    # cached_data = redis_client.get(cache_key)

    # if cached_data:
    #     return jsonify({'source' : 'cache', 
    #                     'data' : json.loads(cached_data)
    #                 }), 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        #total tickets
        if g.role == 'AGENT':
            cursor.execute(
                "SELECT COUNT(*) AS total FROM tickets WHERE created_by = %s",
                (user_id,)
            )
        else:
            cursor.execute("SELECT COUNT(*) AS total FROM tickets")

        total = cursor.fetchone()['total']

        #tickets by status (user specific)
        if g.role == 'AGENT':
            cursor.execute(
                '''SELECT t_status, COUNT(*) AS count 
                FROM tickets 
                WHERE created_by = %s 
                GROUP BY t_status''',
                (user_id,)
            )
        else:
            cursor.execute(
                "SELECT t_status, COUNT(*) AS count FROM tickets GROUP BY t_status"
            )

        status_counts = cursor.fetchall()

        #tickets by priority (user specific)
        if g.role == 'AGENT':
            cursor.execute(
                'SELECT priority, COUNT(*) AS count FROM tickets WHERE created_by = %s GROUP BY priority', (user_id,)
            )
        else:
            cursor.execute("SELECT priority, COUNT(*) AS count FROM tickets GROUP BY priority")

        priority_counts = cursor.fetchall()

        #Top N customers by ticket
        if g.role == "AGENT":
            cursor.execute("""
                SELECT c.c_name, COUNT(t.t_id) AS ticket_count
                FROM tickets t
                JOIN customers c ON t.c_id = c.c_id
                WHERE t.created_by = %s
                GROUP BY c.c_id, c.c_name
                ORDER BY ticket_count DESC
                LIMIT 5
            """, (user_id,))
        else:
            cursor.execute("""
                SELECT c.c_name, COUNT(t.t_id) AS ticket_count
                FROM tickets t
                JOIN customers c ON t.c_id = c.c_id
                GROUP BY c.c_id, c.c_name
                ORDER BY ticket_count DESC
                LIMIT 5
            """)

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