import os
import requests
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any
from dotenv import load_dotenv

# Importaciones del proyecto existente
from Seguridad_base_de_datos.database import get_coneccion_base_de_datos
from Dependencias.dependencias import verificador_usuario

# Carga el archivo .env
load_dotenv()

# Token de MercadoPago desde variable de entorno
ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

# Router con prefijo /api/pagos
router_pagos = APIRouter(prefix="/api/pagos", tags=["Pagos MercadoPago"])


# ─────────────────────────────────────────
# ENDPOINT 1: Crear preferencia de pago
# ─────────────────────────────────────────
@router_pagos.post("/crear")
def crear_pago(
    current_user: dict = Depends(verificador_usuario),
    db: Any = Depends(get_coneccion_base_de_datos)
):
    """
    El frontend llama aqui cuando el alumno da clic en Pagar.
    Obtiene el email del alumno logueado y genera el link de MercadoPago.
    """

    # Obtener email del alumno logueado desde la BD
    cursor = db.cursor()
    cursor.execute(
        "SELECT email FROM users WHERE id = %s",
        (current_user['user_id'],)
    )
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Configurar peticion a MercadoPago
    url = "https://api.mercadopago.com/checkout/preferences"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": f"pago-{current_user['user_id']}"
    }
    data = {
        "items": [{
            "id": "colegiatura-001",
            "title": "Colegiatura Campus Online",
            "description": "Pago mensual",
            "quantity": 1,
            "unit_price": 1500.0,
            "currency_id": "MXN"
        }],
        "payer": {
            "email": user['email']
        },
        "back_urls": {
            "success": "http://localhost:8000/api/pagos/success",
            "failure": "http://localhost:8000/api/pagos/failure",
            "pending": "http://localhost:8000/api/pagos/pending"
        }
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        res_json = response.json()

        if response.status_code != 201:
            return {"error_de_mp": res_json, "status_code": response.status_code}

        return {
            "init_point": res_json.get("init_point"),               # produccion
            "sandbox_init_point": res_json.get("sandbox_init_point") # pruebas
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────
# ENDPOINT 2: Confirmar pago aprobado
# ─────────────────────────────────────────
@router_pagos.get("/success")
def pago_exitoso(
    request: Request,
    db: Any = Depends(get_coneccion_base_de_datos)
):
    """
    MercadoPago redirige aqui cuando el pago fue aprobado.
    Verifica el pago con la API de MercadoPago y actualiza la BD.
    """

    # 1. Obtener payment_id de la URL
    payment_id = request.query_params.get("payment_id")

    if not payment_id:
        raise HTTPException(status_code=400, detail="payment_id no recibido")

    # 2. Verificar con MercadoPago que el pago es real
    try:
        mp_response = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
        )
        data = mp_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 3. Verificar que el estado sea approved
    status_mp = data.get("status")

    if status_mp != "approved":
        return {
            "mensaje": "El pago no fue aprobado",
            "status": status_mp
        }

    # 4. Obtener datos del pago
    monto = data.get("transaction_amount")
    email = data.get("payer", {}).get("email")

    # 5. Mapear status de MercadoPago al formato de la BD
    mapeo_status = {
        "approved":   "paid",
        "rejected":   "failed",
        "pending":    "pending",
        "in_process": "pending",
        "cancelled":  "cancelled"
    }
    status_bd = mapeo_status.get(status_mp, "failed")

    # 6. Verificar que el monto sea correcto
    if monto != 1500.0:
        raise HTTPException(status_code=400, detail="Monto invalido")

    cursor = db.cursor()

    # 7. Verificar si este pago ya fue procesado (evitar duplicados)
    cursor.execute(
        "SELECT id FROM payment_students WHERE external_reference = %s",
        (payment_id,)
    )
    if cursor.fetchone():
        return {"mensaje": "Pago ya procesado anteriormente"}

    # 8. Actualizar PAYMENT_STUDENTS con el pago aprobado
    try:
        cursor.execute("""
            UPDATE payment_students
            SET
                external_reference = %s,
                paid_amount        = %s,
                paid_at            = NOW(),
                payment_method     = 'mercadopago',
                status             = %s
            WHERE student_id = (
                SELECT s.id FROM students s
                JOIN users u ON s.user_id = u.id
                WHERE u.email = %s
            )
            AND status = 'pending'
        """, (payment_id, monto, status_bd, email))

        db.commit()

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "mensaje": "Pago verificado y registrado correctamente",
        "payment_id": payment_id,
        "monto": monto,
        "status": status_bd
    }


# ─────────────────────────────────────────
# ENDPOINT 3: Pago rechazado
# ─────────────────────────────────────────
@router_pagos.get("/failure")
def pago_fallido():
    return {"mensaje": "El pago fue rechazado. Intenta con otro metodo de pago."}


# ─────────────────────────────────────────
# ENDPOINT 4: Pago pendiente
# ─────────────────────────────────────────
@router_pagos.get("/pending")
def pago_pendiente():
    return {"mensaje": "Tu pago esta pendiente de confirmacion."}


# ─────────────────────────────────────────
# ENDPOINT 5: Historial de pagos del alumno
# ─────────────────────────────────────────
@router_pagos.get("/historial")
def historial_pagos(
    current_user: dict = Depends(verificador_usuario),
    db: Any = Depends(get_coneccion_base_de_datos)
):
    """
    Regresa el historial de pagos del alumno logueado.
    Consulta directamente la tabla payment_students.
    """
    cursor = db.cursor()

    cursor.execute("""
        SELECT
            ps.paid_at   AS fecha,
            p.concept    AS descripcion,
            ps.paid_amount AS monto
        FROM payment_students ps
        JOIN payments p ON ps.payment_id = p.id
        JOIN students s ON ps.student_id = s.id
        WHERE s.user_id = %s
        AND ps.status = 'paid'
        ORDER BY ps.paid_at DESC
    """, (current_user['user_id'],))

    pagos = cursor.fetchall()

    return {
        "IdAlumno": current_user['user_id'],
        "Pagos": pagos if pagos else []
    }
