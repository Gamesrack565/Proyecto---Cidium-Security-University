#schemas.py
#Este módulo se encarga de definir los esquemas de datos utilizando Pydantic para lavalidación y serialización de datos en la aplicación.

from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime
from uuid import UUID 

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
    monto_total: float    
    monto_pagado: float   
    estatus: str         

class AlumnoPagosResponse(BaseModel):
    id_alumno: UUID  # Actualizado a UUID
    pagos: List[PagoDetalle]


# --- Agregado para el Módulo de Administrador ---
class AlumnoLista(BaseModel):
    id: UUID
    name: str
    email: str
    student_code: str
    enrollment_status: str

class AdminAlumnosResponse(BaseModel):
    alumnos: List[AlumnoLista]

# --- Agregado para Creación (CRUD) ---
class AlumnoCreate(BaseModel):
    username: str
    email: str
    password: str
    name: str
    student_code: str
    course_level: str

class CargoCreate(BaseModel):
    concept: str
    amount: float
    due_date: date