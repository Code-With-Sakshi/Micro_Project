import mysql.connector

def get_user_certificate_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sakshi",
        database="user_certificate_db"
    )
