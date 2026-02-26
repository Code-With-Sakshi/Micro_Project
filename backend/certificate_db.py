import mysql.connector

def get_certificate_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="sakshi",
        database="certificate_db"
    )
