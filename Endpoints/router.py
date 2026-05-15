#router.py
#Este módulo define las rutas (endpoints) de la API utilizando FastAPI. 
#Agrupa las operaciones de autenticación, administración, portal de alumnos y utilidades del sistema.

#Librerias y módulos:
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from uuid import UUID

#Importaciones de esquemas, conexión a BD y funciones de seguridad propias de la aplicación
import Schemas.schemas as schemas
from Seguridad_base_de_datos.database import get_coneccion_base_de_datos
from Dependencias.dependencias import verificador_usuario, verify_admin_role
from Seguridad_base_de_datos.auth import verificar_contrasena, create_access_token, get_contrasena_hash

#Se inicializa el enrutador principal agregando el prefijo "/api" a todas las rutas definidas aquí
router = APIRouter(prefix="/api")

# ==========================================
# Módulo de Autenticación
# ==========================================

#Procesa el inicio de sesión de un usuario, valida sus credenciales, registra el intento y devuelve un token JWT
@router.post("/auth/login", response_model=schemas.LoginResponse, tags=["Authentication"])
def autenticar_user(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Any = Depends(get_coneccion_base_de_datos)
):
    #Abre un cursor para interactuar con la base de datos
    cursor = db.cursor()
    #Busca al usuario en la base de datos cruzando la tabla de usuarios y roles, ya sea por email o por username
    cursor.execute(
        """SELECT u.id, u.username, u.password_hash, r.name as role 
           FROM users u JOIN roles r ON u.role_id = r.id 
           WHERE u.email = %s OR u.username = %s""", 
        (form_data.username, form_data.username)
    )
    #Obtiene el primer registro que coincida con la búsqueda
    user_db = cursor.fetchone()

    #Obtiene la dirección IP y el agente de usuario (navegador/cliente) para fines de auditoría
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    #Verifica si el usuario no existe o si la contraseña ingresada no coincide con el hash almacenado en la BD
    if not user_db or not verificar_contrasena(form_data.password, user_db['password_hash']):
        #Si el usuario existe pero la contraseña falló, registra el intento fallido en la tabla de logs
        if user_db:
            cursor.execute(
                "INSERT INTO login_logs (user_id, ip_address, user_agent, success) VALUES (%s, %s, %s, False)",
                (user_db['id'], ip_address, user_agent)
            )
            #Guarda los cambios del intento fallido
            db.commit()
        #Lanza una excepción HTTP 401 denegando el acceso
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    #Si la autenticación es correcta, registra el inicio de sesión exitoso en los logs
    cursor.execute(
        "INSERT INTO login_logs (user_id, ip_address, user_agent, success) VALUES (%s, %s, %s, True)",
        (user_db['id'], ip_address, user_agent)
    )
    #Guarda los cambios del inicio de sesión exitoso
    db.commit()

    #Crea el token de acceso JWT utilizando el ID del usuario como identificador (sub)
    access_token = create_access_token(data={"sub": str(user_db['id'])})

    #Retorna la respuesta estructurada según el esquema LoginResponse, incluyendo datos de sesión y el token
    return schemas.LoginResponse(
        success=True,
        message="Inicio de sesión exitoso",
        data=schemas.LoginData(
            session=schemas.UserSessionData(
                user_id=user_db['id'], 
                username=user_db['username'], 
                role=user_db['role']
            ),
            access_token=access_token,
            expires_in=3600
        )
    )

#Cierra la sesión del usuario actual
@router.post("/auth/logout", response_model=schemas.LogoutResponse, tags=["Authentication"])
def logout_user(current_user: dict = Depends(verificador_usuario)):
    #Retorna un mensaje de éxito indicando que la sesión se cerró. La invalidación real del JWT suele hacerse del lado del cliente.
    return schemas.LogoutResponse(success=True, message="Sesión cerrada correctamente")


# ==========================================
# Módulo de Administrador (Reportes y Operaciones)
# ==========================================

#Genera un reporte contabilizando el total de estudiantes activos e inactivos en el sistema
@router.get("/admin/reportes/estudiantes-activos", response_model=schemas.ReporteActivosResponse, tags=["Admin Reports"])
def get_reporte_activos_estudiantes(
    db: Any = Depends(get_coneccion_base_de_datos), 
    admin_user: dict = Depends(verify_admin_role) #Se asegura que solo un administrador acceda
):
    #Abre un cursor para la consulta
    cursor = db.cursor()
    #Construye la consulta para sumar condicionalmente los estados activos e inactivos
    query = """
        SELECT 
            SUM(CASE WHEN u.status = 'active' AND s.enrollment_status = 'active' THEN 1 ELSE 0 END) AS activos,
            SUM(CASE WHEN u.status != 'active' OR s.enrollment_status != 'active' THEN 1 ELSE 0 END) AS inactivos
        FROM users u
        JOIN students s ON u.id = s.user_id;
    """
    #Ejecuta la consulta y obtiene el resultado
    cursor.execute(query)
    result = cursor.fetchone()
    
    #Maneja valores nulos en caso de que la tabla esté vacía, asignando 0 por defecto
    activos = result['activos'] if result['activos'] is not None else 0
    inactivos = result['inactivos'] if result['inactivos'] is not None else 0

    #Retorna la respuesta estructurada con los totales calculados
    return schemas.ReporteActivosResponse(
        numero_de_alumnos_activos=activos, 
        numero_de_alumnos_inactivos=inactivos
    )

#Genera un reporte general de pagos, calculando los montos totales realizados y pendientes
@router.get("/admin/reportes/pagos", response_model=schemas.ReportePagosResponse, tags=["Admin Reports"])
def get_reporte_pagos(db: Any = Depends(get_coneccion_base_de_datos), admin_user: dict = Depends(verify_admin_role)):
    #Abre un cursor y ejecuta la sumatoria de pagos en la tabla payment_students
    cursor = db.cursor()
    cursor.execute("""
        SELECT 
            SUM(paid_amount) AS realizados,
            SUM(assigned_amount - paid_amount) AS pendientes
        FROM payment_students
    """)
    result = cursor.fetchone()
    
    #Verifica valores nulos y establece en 0 si no hay registros
    realizados = result['realizados'] if result['realizados'] is not None else 0
    pendientes = result['pendientes'] if result['pendientes'] is not None else 0
    
    #Retorna el reporte financiero estructurado
    return schemas.ReportePagosResponse(
        sumatoria_pagos_realizados=realizados, 
        sumatoria_pagos_pendientes=pendientes
    )

#Obtiene una lista con todos los estudiantes registrados en la base de datos
@router.get("/admin/estudiantes", response_model=schemas.AdminAlumnosResponse, tags=["Admin Reports"])
def list_todos_estudiantes(db: Any = Depends(get_coneccion_base_de_datos), admin_user: dict = Depends(verify_admin_role)):
    cursor = db.cursor()
    #Cruza la tabla de usuarios con la de estudiantes para traer información básica y de matriculación
    cursor.execute("""
        SELECT u.id, u.name, u.email, s.student_code, s.enrollment_status
        FROM users u
        JOIN students s ON u.id = s.user_id
    """)
    #Obtiene todos los registros encontrados
    alumnos_db = cursor.fetchall()
    #Retorna la lista de alumnos bajo el esquema establecido
    return schemas.AdminAlumnosResponse(alumnos=alumnos_db)

#Crea un nuevo registro de estudiante en la base de datos, generando su usuario y perfil
@router.post("/admin/estudiantes", tags=["Admin Operations"])
def crear_estudiante(
    student_data: schemas.AlumnoCreate,
    db: Any = Depends(get_coneccion_base_de_datos),
    admin_user: dict = Depends(verify_admin_role)
):
    cursor = db.cursor()
    
    #Obtiene el ID de la primera institución disponible como valor por defecto
    cursor.execute("SELECT id FROM institutions LIMIT 1")
    inst_id = cursor.fetchone()['id']
    #Busca y obtiene el ID del rol de "student" para asignarlo al nuevo usuario
    cursor.execute("SELECT id FROM roles WHERE name = 'student'")
    role_id = cursor.fetchone()['id']
    
    #Hashea la contraseña en texto plano provista en los datos del estudiante
    hashed_pw = get_contrasena_hash(student_data.password)
    
    try:
        #Inserta el registro principal en la tabla de usuarios y retorna el ID generado
        cursor.execute("""
            INSERT INTO users (institution_id, role_id, username, email, password_hash, name, status)
            VALUES (%s, %s, %s, %s, %s, %s, 'active') RETURNING id
        """, (inst_id, role_id, student_data.username, student_data.email, hashed_pw, student_data.name))
        new_user_id = cursor.fetchone()['id']
        
        #Con el nuevo ID de usuario, inserta el perfil específico en la tabla de estudiantes
        cursor.execute("""
            INSERT INTO students (user_id, student_code, course_level, enrollment_status)
            VALUES (%s, %s, %s, 'active')
        """, (new_user_id, student_data.student_code, student_data.course_level))
        
        #Aplica los cambios permanentemente en la base de datos
        db.commit()
        return {"message": f"Alumno {student_data.name} registrado correctamente."}
    #Maneja cualquier error de inserción (como duplicados de email o usuario)
    except Exception as e:
        #Revierte cualquier cambio a medias para mantener la consistencia de la BD
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al registrar alumno. Detalle: {str(e)}")

#Crea un nuevo cargo a cobrar y lo asigna automáticamente a todos los estudiantes activos
@router.post("/admin/cargos", tags=["Admin Operations"])
def crear_cargo(
    charge_data: schemas.CargoCreate,
    db: Any = Depends(get_coneccion_base_de_datos),
    admin_user: dict = Depends(verify_admin_role)
):
    cursor = db.cursor()
    
    #Obtiene el ID de la institución por defecto
    cursor.execute("SELECT id FROM institutions LIMIT 1")
    inst_id = cursor.fetchone()['id']
    
    try:
        #Registra el nuevo cargo general en la tabla 'charges' y obtiene su ID
        cursor.execute("""
            INSERT INTO charges (institution_id, concept, amount, currency, due_date, status)
            VALUES (%s, %s, %s, 'MXN', %s, 'pending') RETURNING id
        """, (inst_id, charge_data.concept, charge_data.amount, charge_data.due_date))
        new_charge_id = cursor.fetchone()['id']
        
        #Busca a todos los estudiantes cuyo estado de matrícula sea activo
        cursor.execute("SELECT id FROM students WHERE enrollment_status = 'active'")
        active_students = cursor.fetchall()
        
        #Si no se encuentran estudiantes activos, deshace la creación del cargo y avisa
        if not active_students:
            db.rollback()
            return {"message": "Cargo creado, pero no hay alumnos activos a los cuales asignarlo."}
            
        #Itera sobre cada estudiante activo y le asocia la deuda en la tabla 'payment_students'
        for s in active_students:
            cursor.execute("""
                INSERT INTO payment_students (payment_id, student_id, assigned_amount, paid_amount, status)
                VALUES (%s, %s, %s, 0, 'pending')
            """, (new_charge_id, s['id'], charge_data.amount))
            
        #Si todo sale bien, guarda todos los cambios en cascada
        db.commit()
        return {"message": f"Cargo generado y asignado automáticamente a {len(active_students)} alumnos activos."}
    #Atrapa errores en la transacción
    except Exception as e:
        #Revierte toda la operación para evitar registros huérfanos
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error al generar los cargos. Detalle: {str(e)}")


# ==========================================
# Módulo de Perfiles (Portal Alumno)
# ==========================================

#Obtiene la información del perfil del estudiante que ha iniciado sesión actualmente
@router.get("/estudiantes/me", response_model=schemas.AlumnoMeResponse, tags=["Student Portal"])
def get_perfil_estudiante(current_user: dict = Depends(verificador_usuario), db: Any = Depends(get_coneccion_base_de_datos)):
    cursor = db.cursor()
    #Busca los datos personales y académicos cruzando las tablas usando el ID del token actual
    cursor.execute("""
        SELECT u.name as nombre, s.course_level as curso, s.enrollment_status as status
        FROM users u
        JOIN students s ON u.id = s.user_id
        WHERE u.id = %s
    """, (current_user['user_id'],))
    
    perfil = cursor.fetchone()
    #Si por alguna razón no se halla el perfil, se lanza un error 404
    if not perfil:
        raise HTTPException(status_code=404, detail="Perfil de alumno no encontrado")
        
    #Retorna la información utilizando la desestructuración del diccionario al esquema
    return schemas.AlumnoMeResponse(**perfil)

#Obtiene el historial de pagos y cargos asociados al estudiante que ha iniciado sesión
@router.get("/estudiantes/me/pagos", response_model=schemas.AlumnoPagosResponse, tags=["Student Portal"])
def get_historial_pago_estudiantes(current_user: dict = Depends(verificador_usuario), db: Any = Depends(get_coneccion_base_de_datos)):
    cursor = db.cursor()
    #Relaciona la tabla de pagos asignados con los cargos y el perfil del alumno para obtener un historial detallado
    cursor.execute("""
        SELECT 
            c.due_date as fecha, 
            c.concept as descripcion, 
            ps.assigned_amount as monto_total,
            ps.paid_amount as monto_pagado,
            ps.status as estatus
        FROM payment_students ps
        JOIN students s ON ps.student_id = s.id
        JOIN charges c ON ps.payment_id = c.id
        WHERE s.user_id = %s
    """, (current_user['user_id'],))
    
    #Trae todos los registros de pagos de este alumno en particular
    pagos_db = cursor.fetchall()
    
    #Retorna el ID del alumno y la lista de pagos mapeada al esquema de respuesta
    return schemas.AlumnoPagosResponse(
        id_alumno=current_user['user_id'], 
        pagos=pagos_db
    )


# ==========================================
# Utilidades de Sistema (Temporales) - NO SE UTILIZA, PERO LO DEJO PARA QUE SE PONGA EN EL REPORTE 
# ==========================================

#Ruta de utilidad para forzar o restablecer la contraseña del superadministrador inicial
#@router.post("/system/setup-admin-password", tags=["System"])
#def setup_admin_password(db: Any = Depends(get_coneccion_base_de_datos)):
#    cursor = db.cursor()
#    #Genera el hash seguro para la contraseña predefinida "admin123"
#    real_hash = get_contrasena_hash("admin123")
    
    #Actualiza la contraseña en la base de datos donde el username sea "superadmin1"
#    cursor.execute(
#        "UPDATE users SET password_hash = %s WHERE username = 'superadmin1'", 
#        (real_hash,)
#    )
    #Guarda la actualización
#    db.commit()
#    return {"message": "Contraseña de superadmin1 actualizada a 'admin123' exitosamente."}