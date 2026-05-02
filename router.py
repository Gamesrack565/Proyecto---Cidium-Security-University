from fastapi import APIRouter, Depends, HTTPException
from typing import Any
from uuid import UUID
import schemas
from database import get_db_connection
from dependencias import verify_current_user, verify_admin_role

router = APIRouter(prefix="/api")

# ==========================================
# Módulo de Autenticación
# ==========================================
@router.post("/auth/login", response_model=schemas.LoginResponse, tags=["Authentication"])
def authenticate_user(request: schemas.LoginRequest, db: Any = Depends(get_db_connection)):
    # Mock Response con un UUID válido
    return schemas.LoginResponse(
        success=True,
        message="Inicio de sesión exitoso",
        data=schemas.LoginData(
            session=schemas.UserSessionData(
                user_id=UUID("a1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d"), 
                username="jperez", 
                role="student"
            ),
            access_token="eyJhbGciOiJIUzI1NiIsInR...",
            expires_in=3600
        )
    )

@router.post("/auth/logout", response_model=schemas.LogoutResponse, tags=["Authentication"])
def logout_user(current_user: dict = Depends(verify_current_user)):
    return schemas.LogoutResponse(success=True, message="Sesión cerrada correctamente")

@router.get("/auth/me", response_model=schemas.MeResponse, tags=["Authentication"])
def get_current_user_profile(current_user: dict = Depends(verify_current_user), db: Any = Depends(get_db_connection)):
    pass # Reemplazar con lógica real

# ==========================================
# Módulo de Administrador
# ==========================================
@router.get("/admin/reports/active-students", response_model=schemas.ReporteActivosResponse, tags=["Admin Reports"])
def get_active_students_report(
    db: Any = Depends(get_db_connection), 
    admin_user: dict = Depends(verify_admin_role)
):
    return schemas.ReporteActivosResponse(numero_de_alumnos_activos=150, numero_de_alumnos_inactivos=12)

@router.get("/admin/reports/payments", response_model=schemas.ReportePagosResponse, tags=["Admin Reports"])
def get_payments_report(db: Any = Depends(get_db_connection), admin_user: dict = Depends(verify_admin_role)):
    return schemas.ReportePagosResponse(sumatoria_pagos_realizados=45000.50, sumatoria_pagos_pendientes=12000.00)

# ==========================================
# Módulo de Perfiles (Alumnos)
# ==========================================
@router.get("/students/me", response_model=schemas.AlumnoMeResponse, tags=["Student Portal"])
def get_student_profile(current_user: dict = Depends(verify_current_user), db: Any = Depends(get_db_connection)):
    return schemas.AlumnoMeResponse(nombre="Angel Higuera", curso="Ingeniería en IA", status="Activo")

@router.get("/students/me/payments", response_model=schemas.AlumnoPagosResponse, tags=["Student Portal"])
def get_student_payment_history(current_user: dict = Depends(verify_current_user), db: Any = Depends(get_db_connection)):
    pagos_mock = [
        schemas.PagoDetalle(fecha="2026-03-01", descripcion="Colegiatura Marzo", monto=2500.00),
        schemas.PagoDetalle(fecha="2026-04-01", descripcion="Colegiatura Abril", monto=2500.00)
    ]
    return schemas.AlumnoPagosResponse(id_alumno=current_user["user_id"], pagos=pagos_mock)