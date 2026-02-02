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
    cache_key = f"dashboard:{g.role}:{g.user_id}"

    cached_data = redis_client.get(cache_key)

    if cached_data:
        return jsonify({'source' : 'cache', 'data' : 'json.loads(cached_data)'}), 200
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        #Agent dashboard
        if g.role == 'AGENT':

            #total tickets created by agent
            cursor.execute(
                'SELECT (*) AS total from tickets WHERE created_by = %s', (g.user_id,)
            )
            total  = cursor.fetchone()['total']

            #tickets by status
            cursor.execute("""SELECT t_status, COUNT(*) AS count from tickets WHERE created_by = %s GROUP BY t_status""", (g.user_id,)
            )
            status_counts = cursor.fetchall()

            #tickets by priority
            cursor.execute("""SELECT priority, COUNT(*) AS count from tickets WHERE created_by = %s GROUP BY priority""", (g.user_id,)
            )
            priority_counts = cursor.fetchall()
            
            #total tickets created by agent
            cursor.execute(
                'SELECT (*) AS total from customers WHERE created_by = %s', (g.user_id,)
            )
            total_customers  = cursor.fetchone()['total']

        #Admin/Team-Lead dashboard
        else:
            cursor.execute("SELECT COUNT(*) AS total FROM tickets")    
            total = cursor.fetchone()['total']

            cursor.execute("""SELECT t_status, COUNT(*) AS count FROM tickets GROUP BY t_status""")
            status_counts = cursor.fetchall()

            cursor.execute("""SELECT priority, COUNT(*) AS count FROM tickets GROUP BY priority""")
            priority_counts = cursor.fetchall()

            cursor.execute("SELECT COUNT(*) AS total FROM customers")
            total_customers = cursor.fetchall()['total']

        result = {
            'total_tickets': total,
            'tickets_by_status' : status_counts,
            'tickets_by_priority' : priority_counts,
            'total_customers' : total_customers
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