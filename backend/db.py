import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connetion = mysql.connector.connect(
            user='root',
            password='root',
            host='localhost',
            database='support_desk'
        )

        return connetion
    
    except Error as e:
        print("Database error", e)

        