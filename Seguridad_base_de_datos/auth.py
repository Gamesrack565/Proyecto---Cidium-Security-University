#auth.py
#Este módulo se encarga de manejar la autenticación y generación de tokens JWT para la aplicación

import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from dotenv import load_dotenv

load_dotenv()

#Configuracion de parametros:
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM") 
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

#Verifica la contraseña en texto plano con su hash almacenado en la BD utilizando el esquema de hashing configurado
def verificar_contrasena(plain_password: str, hashed_password: str) -> bool:
    #Retorna True si la contraseña en texto plano coincide con el hash almacenado, y False en caso contrario
    return pwd_context.verify(plain_password, hashed_password)

#Obtiene el hash de una contraseña en texto plano utilizando el esquema de hashing configurado
def get_contrasena_hash(password: str) -> str:
    #Retorna el hash de la contraseña en texto plano, que se puede almacenar de forma segura en la base de datos
    return pwd_context.hash(password)

#Crea un Token JWT (JSON Web Token) con tiempo de expiración.
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    #Copia los datos proporcionados en un nuevo diccionario que se utilizará para construir el payload del token
    to_encode = data.copy()
    #Si se proporciona un tiempo de expiración personalizado, se calcula la fecha y hora de expiración sumando el tiempo actual con el tiempo proporcionado. 
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    #Si no se proporciona un tiempo de expiración, se establece un valor predeterminado utilizando la configuración ACCESS_TOKEN_EXPIRE_MINUTES
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    #Agrega la fecha y hora de expiración al payload del token bajo la clave "exp" (expiration)
    to_encode.update({"exp": expire})
    #Codifica el payload utilizando la clave secreta y el algoritmo de firma configurados, generando un token JWT que se puede enviar al cliente para autenticación
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt