#dependencias.py
#Este módulo se encarga de manejar las dependencias de autenticación y autorización en la aplicación

#Librerias:
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Any
from Seguridad_base_de_datos.auth import SECRET_KEY, ALGORITHM
from Seguridad_base_de_datos.database import get_coneccion_base_de_datos

#Generador de token de segruidad, utilizando el esquema de OAuth2 con contraseña y token de portador
#Se le indica la ruta del endpoint de login para obtener el token, que es "api/auth/login" en este caso
#oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/auth/login")
security = HTTPBearer()

#Verificador de usuario, que se encarga de validar el token de seguridad y verificar que el usuario esté activo en la base de datos
def verificador_usuario(
    #Obtiene el token de seguridad del encabezado de autorización utilizando el esquema de OAuth2 definido anteriormente
    credentials: HTTPAuthorizationCredentials = Depends(security),
    #Conección con la base de datos 
    db: Any = Depends(get_coneccion_base_de_datos)
):  
    #Definimos una excepción de credenciales que se lanzará si el token no es válido o si el usuario no tiene los permisos necesarios
    credentials_exception = HTTPException(
        #Estado de error HTTP 401 (No autorizado) si las credenciales no son válidas
        status_code=status.HTTP_401_UNAUTHORIZED,
        #Detalle del error que se muestra al cliente cuando las credenciales no son válidas
        detail="No se pudieron validar las credenciales",
        #Encabezado de autenticación que indica que se requiere un token de portador para acceder al recurso protegido
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Extraemos el token limpio que vas a pegar en Swagger
    token = credentials.credentials

    try:
        #Desencriptamos el token usando la configuracion de autenticación definida en auth.py (SECRET_KEY y ALGORITHM)
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        #Obtenemos el ID del usuario del payload del token, que se encuentra en el campo "sub" (subject)
        user_id: str = payload.get("sub")
        #Si el ID del usuario no se encuentra en el token, se lanza la excepción de credenciales definida anteriormente
        if user_id is None:
            raise credentials_exception
    #Si ocurre un error al decodificar el token (por ejemplo, si el token es inválido o ha expirado), se lanza la excepción de credenciales definida anteriormente
    except JWTError:
        raise credentials_exception

    #Vamos a la base de datos a verificar que el usuario siga activo y traemos su rol
    cursor = db.cursor()
    #Ejecutamos una consulta SQL para obtener el ID del usuario, 
    # su nombre de usuario y su rol, uniendo las tablas "users" 
    # y "roles" en función del ID del rol. La consulta también verifica que el usuario tenga un estado "active".
    cursor.execute("""
        SELECT u.id as user_id, u.username, r.name as role 
        FROM users u 
        JOIN roles r ON u.role_id = r.id 
        WHERE u.id = %s AND u.status = 'active'
    """, (user_id,))
    #Obtenemos el resultado de la consulta
    user_data = cursor.fetchone()
    #Si no se encuentra ningún usuario que coincida con el ID proporcionado y que tenga un estado "active", se lanza la excepción de credenciales definida anteriormente
    if user_data is None:
        raise credentials_exception
    #Retornamos un diccionario con la informacion del usuario
    return dict(user_data)

#Verificador de rol de administrador, que se encarga de verificar que el usuario tenga el rol de "superadmin" para acceder a ciertos recursos protegidos
#Depende del verificador de usuario para obtener la información del usuario autenticado y verificar su rol
def verify_admin_role(current_user: dict = Depends(verificador_usuario)):
    #Si su rol no es "superadmin", se lanza una excepción HTTP 403 (Prohibido) indicando que se requieren privilegios de administrador para acceder al recurso protegido
    if current_user.get("role") != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren privilegios de administrador"
        )
    return current_user