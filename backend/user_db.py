import mysql.connector

def get_user_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Add_Password",
        database="user_db"
    )
