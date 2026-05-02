import psycopg2
from psycopg2.extras import RealDictCursor
import os

#SE NECESITAN LOS DATOS DE CONEXIÓN A LA BASE DE DATOS EN VARIABLES DE ENTORNO
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "school_platform")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "tu_password_aqui")

def get_db_connection():
    conn = None
    try:
        # Se establece la conexión a PostgreSQL
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor # Convierte los resultados a diccionarios
        )
        yield conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        raise e
    finally:
        if conn is not None:
            conn.close()