import os
import psycopg2
from dotenv import load_dotenv


#Tener instalado: pip install psycopg2-binary


# Carga las variables de entorno desde un archivo .env si existe
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Script SQL auto-contenido
SQL_SCRIPT = """
-- ============================================================
-- 1. LIMPIEZA DE TABLAS EXISTENTES (ELIMINACIÓN EN CASCADA)
-- ============================================================
DROP TABLE IF EXISTS login_logs CASCADE;
DROP TABLE IF EXISTS payment_students CASCADE;
DROP TABLE IF EXISTS charges CASCADE;
DROP TABLE IF EXISTS students CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS roles CASCADE;
DROP TABLE IF EXISTS institutions CASCADE;

-- ============================================================
-- 2. CREACIÓN DE LA ESTRUCTURA DE LA BASE DE DATOS
-- ============================================================

CREATE TABLE institutions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    tuition_fee DECIMAL(10, 2) DEFAULT 1500.0, -- Cuota global actualizable
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id) ON DELETE SET NULL,
    role_id UUID REFERENCES roles(id) ON DELETE SET NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'active',
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    student_code VARCHAR(100) UNIQUE NOT NULL,
    course_level VARCHAR(100),
    enrollment_status VARCHAR(50) DEFAULT 'active'
);

CREATE TABLE charges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    institution_id UUID REFERENCES institutions(id) ON DELETE CASCADE,
    concept VARCHAR(255) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'MXN',
    due_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE payment_students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID REFERENCES charges(id) ON DELETE CASCADE,
    student_id UUID REFERENCES students(id) ON DELETE CASCADE,
    assigned_amount DECIMAL(10, 2) NOT NULL,
    paid_amount DECIMAL(10, 2) DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'paid', 'failed'
    paid_at TIMESTAMP,
    external_reference VARCHAR(255),       -- ID de transacción de pasarela (MercadoPago)
    payment_method VARCHAR(50)
);

CREATE TABLE login_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    success BOOLEAN,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 3. INSERCIÓN DE DATOS INICIALES SEMILLA (SEEDERS)
-- ============================================================

-- Institución inicial con la cuota base
INSERT INTO institutions (name, tuition_fee) 
VALUES ('Campus Online EduCore', 1500.0);

-- Roles del sistema
INSERT INTO roles (name, description) VALUES ('admin', 'Administrador del sistema');
INSERT INTO roles (name, description) VALUES ('student', 'Estudiante regular');

-- Cuenta de Super Administrador Inicial
-- Nota: El password_hash corresponde a 'admin123' encriptado de forma compatible con la aplicación (Bcrypt/Argon2)
INSERT INTO users (institution_id, role_id, username, email, password_hash, name, status)
VALUES (
    (SELECT id FROM institutions LIMIT 1),
    (SELECT id FROM roles WHERE name = 'admin'),
    'superadmin1',
    'admin@educore.com',
    '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjIQqiRQYq', 
    'Administrador Principal',
    'active'
);
"""

def inicializar_base_de_datos():
    print("Iniciando la limpieza y recreación de la base de datos...")
    
    # Validación básica de variables de entorno antes de intentar la conexión
    if not all([DB_HOST, DB_NAME, DB_USER, DB_PASSWORD]):
        print("Error: Faltan variables de entorno de conexión en el sistema.")
        return

    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT or "5432",
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        
        # Ejecución del bloque de código SQL completo
        cursor.execute(SQL_SCRIPT)
        conn.commit()
        
        print("Base de datos reconstruida con éxito desde cero.")
        print("Estructura creada e inserciones iniciales completadas correctamente.")
        
    except Exception as e:
        print(f"Ocurrió un error crítico durante la inicialización: {e}")
        if conn is not None:
            conn.rollback()
    finally:
        if conn is not None:
            conn.close()

if __name__ == "__main__":
    inicializar_base_de_datos()