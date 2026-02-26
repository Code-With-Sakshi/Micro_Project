import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="sakshi",
        database="microproject_db"
    )
    return connection




