import os
import mysql.connector
from dotenv import load_dotenv

def obtener_conexion():
    """Carga las variables de entorno y retorna la conexión a MySQL."""
    load_dotenv()
    
    try:
        conexion = mysql.connector.connect(
            host=os.getenv('DB_HOST', '127.0.0.1'),
            database=os.getenv('DB_NAME', 'loterias_db'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        return conexion
    except mysql.connector.Error as error:
        print(f"❌ Error crítico conectando a la base de datos: {error}")
        return None