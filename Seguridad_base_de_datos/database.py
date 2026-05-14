#database.py
#Este módulo se encarga de manejar la conexión a la base de datos PostgreSQL utilizando psycopg2.

#Librerias:
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

#Carga las variables desde el archivo .env
load_dotenv()
#Dichas variables de entorno, cuentan con la información dada por la base de datos
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


def get_coneccion_base_de_datos():
    #Se crea la variable de coneccion.
    conecc = None
    try:
        #Se intenta establecer la coneccion a la base de datos utilizando las variables de entorno
        conecc = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor 
        )
        #Si la coneccion es exitosa, se devuelve el objeto de coneccion para ser utilizado en las operaciones de la base de datos
        yield conecc
    #En caso de que ocurra un error en la coneccion
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}")
        #Detiene la ejecución y lanza el error para que sea manejado por el llamador
        raise e
    #Finalmente, se asegura de cerrar la coneccion a la base de datos después de que se hayan completado las operaciones, incluso si ocurre un error
    finally:
        if conecc is not None:
            conecc.close()