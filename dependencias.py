from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

# Renombramos a algo más estandarizado
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def verify_current_user(token: str = Depends(oauth2_bearer)):
    # Aquí iría la lógica para decodificar tu JWT
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # Mock: Retornamos un UUID válido para que coincida con tu schema
    return {
        "user_id": UUID("123e4567-e89b-12d3-a456-426614174000"), 
        "role": "admin", 
        "username": "admin_user"
    }

def verify_admin_role(current_user: dict = Depends(verify_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción"
        )
    return current_user