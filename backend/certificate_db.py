import mysql.connector

def get_certificate_connection():

    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Add_Password",
        database="certificate_db"
    )
