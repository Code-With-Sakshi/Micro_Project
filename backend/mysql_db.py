import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Add_Password",
        database="microproject_db"
    )
    return connection




