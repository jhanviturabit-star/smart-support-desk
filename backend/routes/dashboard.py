import mysql.connector, json
from flask import jsonify, Flask, request, Blueprint
from pydantic import ValidationError
from db import get_db_connection
from redis_client import redis_client
from auth.decorators import require_roles

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/', methods=['GET'])
@require_roles('ADMIN', 'TEAM_LEAD')
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
        total = cursor.fetchone()['total']

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