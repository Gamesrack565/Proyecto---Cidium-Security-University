from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID # <-- Importación necesaria para la nueva base de datos

# --- Módulo de Administrador ---
class ReporteActivosResponse(BaseModel):
    numero_de_alumnos_activos: int
    numero_de_alumnos_inactivos: int

class ReportePagosResponse(BaseModel):
    sumatoria_pagos_realizados: float
    sumatoria_pagos_pendientes: float

# --- Módulo de Autenticación ---
class LoginRequest(BaseModel):
    email: str
    password: str

class UserSessionData(BaseModel):
    user_id: UUID  # Actualizado a UUID
    username: str
    role: str

class LoginData(BaseModel):
    session: UserSessionData
    access_token: str
    token_type: str = "Bearer"
    expires_in: int

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[LoginData] = None

class LogoutResponse(BaseModel):
    success: bool
    message: str

class UserMe(BaseModel):
    id: UUID  # Actualizado a UUID
    username: str
    email: str
    name: str
    status: str
    last_login_at: Optional[datetime] # Puede ser nulo si es su primer login
    created_at: datetime

class RoleMe(BaseModel):
    id: UUID  # Actualizado a UUID
    name: str
    description: Optional[str]

class MeData(BaseModel):
    user: UserMe
    role: RoleMe

class MeResponse(BaseModel):
    success: bool
    data: MeData

# --- Módulo de Perfiles ---
class AlumnoMeResponse(BaseModel):
    nombre: str
    curso: str
    status: str

class PagoDetalle(BaseModel):
    fecha: date
    descripcion: str
    monto: float

class AlumnoPagosResponse(BaseModel):
    id_alumno: UUID  # Actualizado a UUID
    pagos: List[PagoDetalle]