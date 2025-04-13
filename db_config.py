import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",  # Si tienes contraseña en tu MySQL, escríbela aquí
        database="inventario_pg"
    )