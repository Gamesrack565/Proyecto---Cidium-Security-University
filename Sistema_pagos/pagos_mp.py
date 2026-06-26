import os
import requests
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any
from dotenv import load_dotenv

# Importaciones
from Seguridad_base_de_datos.database import get_coneccion_base_de_datos
from Dependencias.dependencias import verificador_usuario

# Carga el archivo .env
load_dotenv()

ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN")

router_pagos = APIRouter(prefix="/api/pagos", tags=["Pagos MercadoPago"])

# ─────────────────────────────────────────
# ENDPOINT 1: Crear preferencia de pago
# ─────────────────────────────────────────
@router_pagos.post("/crear")
def crear_pago(
    current_user: dict = Depends(verificador_usuario),
    db: Any = Depends(get_coneccion_base_de_datos)
):
    cursor = db.cursor()
    
    # 1. Obtener email del usuario
    cursor.execute("SELECT email FROM users WHERE id = %s", (current_user['user_id'],))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # 2. Obtener el cargo pendiente de este alumno directamente de la base de datos
    cursor.execute("""
        SELECT ps.assigned_amount, c.concept 
        FROM payment_students ps
        JOIN students s ON ps.student_id = s.id
        JOIN charges c ON ps.payment_id = c.id
        WHERE s.user_id = %s AND ps.status = 'pending'
        LIMIT 1
    """, (current_user['user_id'],))
    
    cargo = cursor.fetchone()
    if not cargo:
        raise HTTPException(status_code=400, detail="No tienes cargos pendientes por pagar.")

    monto_a_pagar = float(cargo['assigned_amount'])
    concepto_pago = cargo['concept']

    # 3. Configurar peticion a MercadoPago con los datos dinámicos
    url = "https://api.mercadopago.com/checkout/preferences"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Idempotency-Key": str(uuid.uuid4())
    }
    data = {
        "items": [{
            "id": "colegiatura-dinamica",
            "title": concepto_pago,
            "description": "Pago de colegiatura",
            "quantity": 1,
            "unit_price": monto_a_pagar, 
            "currency_id": "MXN"
        }],
        "payer": {
            "email": user['email']
        },
    "external_reference": str(current_user['user_id']),
    "back_urls": {
    "success": "http://localhost:5173/pago/exitoso",
    "failure": "http://localhost:5173/pago/fallido",
    "pending": "http://localhost:5173/pago/pendiente"
}
      #  "auto_return": "approved"
    }

    try:
        response = requests.post(url, json=data, headers=headers)
        res_json = response.json()
        if response.status_code != 201:
            return {"error_de_mp": res_json, "status_code": response.status_code}

        return {
            "init_point": res_json.get("init_point"),
            "sandbox_init_point": res_json.get("sandbox_init_point")
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
    payment_id = request.query_params.get("payment_id")
    if not payment_id:
        raise HTTPException(status_code=400, detail="payment_id no recibido")

    try:
        mp_response = requests.get(
            f"https://api.mercadopago.com/v1/payments/{payment_id}",
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"}
        )
        data = mp_response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    status_mp = data.get("status")
    if status_mp != "approved":
        return {"mensaje": "El pago no fue aprobado", "status": status_mp}

    monto = float(data.get("transaction_amount"))
    user_id_pago = data.get("external_reference")
    
    if not user_id_pago:
        raise HTTPException(status_code=400, detail="El pago no tiene external_reference, no se puede identificar al alumno.")

    cursor = db.cursor()

    # Buscar en la BD cuánto debía este alumno realmente (por user_id, no por email)
    cursor.execute("""
        SELECT ps.assigned_amount 
        FROM payment_students ps
        JOIN students s ON ps.student_id = s.id
        WHERE s.user_id = %s AND ps.status = 'pending'
    """, (user_id_pago,))

    cargo_esperado = cursor.fetchone()
    if not cargo_esperado:
        raise HTTPException(status_code=400, detail="No se encontró un cargo pendiente para este usuario.")

    if monto != float(cargo_esperado['assigned_amount']):
        raise HTTPException(status_code=400, detail=f"Monto invalido. Se esperaban {cargo_esperado['assigned_amount']} pero se pagaron {monto}")

    cursor.execute("SELECT id FROM payment_students WHERE external_reference = %s", (payment_id,))
    if cursor.fetchone():
        return {"mensaje": "Pago ya procesado anteriormente"}

    try:
        cursor.execute("""
            UPDATE payment_students
            SET external_reference = %s, paid_amount = %s, paid_at = NOW(), payment_method = 'mercadopago', status = 'paid'
            WHERE student_id = (SELECT s.id FROM students s WHERE s.user_id = %s)
            AND status = 'pending'
        """, (payment_id, monto, user_id_pago))
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "mensaje": "Pago verificado y registrado correctamente",
        "payment_id": payment_id,
        "monto": monto,
        "status": "paid"
    }

# ─────────────────────────────────────────
# ENDPOINT 3, 4 y 5
# ─────────────────────────────────────────
@router_pagos.get("/failure")
def pago_fallido():
    return {"mensaje": "El pago fue rechazado. Intenta con otro metodo de pago."}

@router_pagos.get("/pending")
def pago_pendiente():
    return {"mensaje": "Tu pago esta pendiente de confirmacion."}

@router_pagos.get("/historial")
def historial_pagos(current_user: dict = Depends(verificador_usuario), db: Any = Depends(get_coneccion_base_de_datos)):
    cursor = db.cursor()
    cursor.execute("""
        SELECT ps.paid_at AS fecha, p.concept AS descripcion, ps.paid_amount AS monto
        FROM payment_students ps
        JOIN charges p ON ps.payment_id = p.id
        JOIN students s ON ps.student_id = s.id
        WHERE s.user_id = %s AND ps.status = 'paid'
        ORDER BY ps.paid_at DESC
    """, (current_user['user_id'],))
    pagos = cursor.fetchall()
    return {"IdAlumno": current_user['user_id'], "Pagos": pagos if pagos else []}
