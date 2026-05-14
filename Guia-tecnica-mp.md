# Manual Técnico: Backend API REST y Despliegue en la Nube (EduCore MVP)

## Índice
* [Resumen ejecutivo y vision del sistema](#resumen-ejecutivo-y-visión-del-sistema)
* [1. Arquitectura y Proceso de Despliegue](#1-arquitectura-y-proceso-de-despliegue)
* [2. Explicación de la Estructura del Código](#2-explicación-de-la-estructura-del-código)
* [3. Resumen de Endpoints de la API](#3-resumen-de-endpoints-de-la-api)
* [4. Requerimientos de Base de Datos](#4-requerimientos-de-base-de-datos)
* [5. Configuración de Infraestructura y Despliegue](#5-configuración-de-infraestructura-y-despliegue)
* [6. Gestión de Errores y Glosario Técnico](#6-gestión-de-errores-y-glosario-técnico)
* [7. Requerimientos y Conexión con Frontend](#7-requerimientos-y-conexión-con-frontend)
* [8. Análisis de Integración y Discrepancias](#8-análisis-de-integración-y-discrepancias)

---

## Resumen Ejecutivo y Visión del Sistema

EduCore MVP es una plataforma robusta de gestión académica y financiera. El backend ha sido diseñado bajo los principios de **escalabilidad vertical** y **seguridad por diseño**. La API actúa como el orquestador central que comunica la interfaz de usuario (React) con los servicios de datos en Azure y los servicios financieros de MercadoPago.

**Stack Tecnológico Seleccionado:**
- **FastAPI:** Elegido por su manejo asíncrono (ASGI), lo que permite procesar múltiples peticiones de pago y consultas de reportes simultáneamente sin bloquear el hilo principal.
- **Pydantic:** Utilizado para la validación de esquemas, asegurando que los datos que entran a la base de datos sean 100% íntegros.
- **SQL (PostgreSQL):** Motor relacional para garantizar la consistencia ACID en las transacciones financieras.


## 1. Arquitectura y Proceso de Despliegue

Para la construcción del backend del proyecto EduCore MVP, se diseñó una arquitectura basada en microservicios utilizando **Python y FastAPI**, conectada a una base de datos relacional PostgreSQL alojada en **Microsoft Azure**, y desplegada en producción a través de contenedores Docker en **Hugging Face Spaces**.

### 1.1 Entorno de Producción (Hugging Face Spaces)
El servidor en vivo se encuentra alojado en un Space configurado con Docker. 

| Dato | Valor |
|------|-------|
| **Tecnología Core** | Python 3.12 + FastAPI |
| **Servidor ASGI** | Uvicorn (Puerto expuesto: 7860) |
| **URL Base de la API** | `https://bitgames456-proyecto-cidium.hf.space` |
| **Documentación Viva** | `/docs` (Swagger UI) |

### 1.2 Proceso de Despliegue en la Nube

1. **Configuración del Dockerfile:** Se instruye a Hugging Face para construir la imagen instalando las dependencias del archivo `requirements.txt` y exponiendo el puerto `7860`, requerido estrictamente por la plataforma.
2. **Protección de Credenciales (Secrets):** Para evitar la exposición del archivo `.env` en un repositorio público, las credenciales de Azure se inyectaron directamente en la configuración del Space en Hugging Face.

> **[INSERTA AQUÍ IMAGEN DE: Captura de pantalla de la sección "Variables and secrets" en los Settings de Hugging Face]**

3. **Verificación de Salud:** Una vez que el contenedor marca "Running", se accede al endpoint de salud para confirmar la conexión.

> **[INSERTA AQUÍ IMAGEN DE: Captura de pantalla de la respuesta GET /health devolviendo {"status": "ok"}]**

---

## 2. Explicación de la Estructura del Código

El backend está fuertemente modularizado para separar la configuración del servidor, la gestión de rutas (routers) y la seguridad, permitiendo una fácil escalabilidad.

### 2.1 Archivo Principal (`main.py`)
Es el punto de entrada de la aplicación. Sus responsabilidades principales son:
* Inicializar la aplicación FastAPI.
* Configurar las políticas **CORS (Cross-Origin Resource Sharing)**, permitiendo que el Frontend (React) se comunique con el servidor desde un dominio distinto.
* **Unificar los Enrutadores:** Utiliza `app.include_router()` para ensamblar los distintos módulos de la aplicación (`router` y `router_pagos`) en un solo servidor.

### 2.2 Gestión de Enrutadores (`router.py` y `pagos_mp.py`)
Para mantener el código limpio, las rutas no se escriben en el archivo principal, sino que se dividen en submódulos utilizando `APIRouter`:

1.  **Enrutador Core (`router.py`):** Agrupa la lógica principal del sistema. Todos sus endpoints heredan el prefijo `/api`.
    * **Módulo de Autenticación:** Verifica credenciales en Azure, genera tokens JWT y registra logs de acceso.
    * **Módulo de Administrador:** Protegido por roles. Permite gestionar estudiantes y cargos masivos.
    * **Módulo de Portal Alumno:** Protegido por sesión. Devuelve información específica del alumno autenticado.
2.  **Enrutador de Pagos (`pagos_mp.py`):** Módulo dedicado exclusivamente a la integración financiera. Utiliza el prefijo `/api/pagos` y aísla toda la lógica de conexión con la API de MercadoPago, generación de *Checkout Pro* y manejo de *Webhooks* (respuestas de éxito/fallo).

### 2.3 Seguridad y Dependencias (`auth.py` y `dependencias.py`)
El flujo de seguridad funciona así:
1. El usuario envía credenciales; la API valida la contraseña con el hash (`passlib`).
2. Se firma un JWT (`python-jose`) con la `SECRET_KEY`.
3. En peticiones posteriores, `verificador_usuario` o `verify_admin_role` extraen el JWT del header `Authorization`, lo decodifican y autorizan la operación según el rol.

---

## 3. Resumen de Endpoints de la API

La API cuenta con documentación autogenerada bajo el estándar OpenAPI (Swagger UI). 

> **[INSERTA AQUÍ IMAGEN DE: image_bf285c.png - Captura general del Swagger mostrando todas las categorías (Authentication, Admin Reports, Admin Operations, Student Portal, Pagos MercadoPago)]**

### 3.1 Autenticación y Sistema
El endpoint `/api/auth/login` es la puerta de entrada. Trabaja bajo el estándar **OAuth2 con Password Flow**.

**Cómo funciona internamente:**
1. **Recepción:** Recibe un formulario (no JSON) con `username` y `password`.
2. **Búsqueda Dual:** El sistema busca en Azure si el dato coincide con un `username` o con un `email`.
3. **Verificación Criptográfica:** Se utiliza `passlib` para comparar la contraseña plana contra el Hash almacenado (Bcrypt).
4. **Tokenización:** Si es válido, se genera un **JWT (JSON Web Token)** firmado con una clave secreta. Este token es el que el frontend usará para "identificarse" en cada clic posterior.
5. **Auditoría:** Se registra un log en la tabla `login_logs` con la IP del solicitante y el resultado del intento.


| Método | Ruta | Headers/Body | Para qué sirve |
|---|---|---|---|
| GET | `/health` | Ninguno | Verifica que el servidor está en línea. |
| POST | `/api/auth/login` | `x-www-form-urlencoded` | Valida credenciales y devuelve el Token JWT. |
| POST | `/api/auth/logout` | `Authorization: Bearer` | Invalida la sesión actual del usuario. |

### 3.2 Operaciones de Administrador
Este módulo utiliza **SQL Agregado** para generar inteligencia de negocio en tiempo real.

- **Reportes de Alumnos (`/admin/reportes/estudiantes-activos`)**: Utiliza la cláusula `SUM(CASE WHEN ...)` para que la base de datos haga el conteo pesado y entregue solo el resultado final a la API, optimizando el ancho de banda.
- **Creación de Alumnos (`/admin/estudiantes`)**: Implementa una **Transacción Atómica**. Primero crea el usuario en la tabla `users`, obtiene el ID generado, y solo si eso funciona, crea el perfil en la tabla `students`. Si algo falla, se hace un `rollback` automático para no dejar datos huérfanos.

*Requieren token de sesión con rol `superadmin` o `admin`.*

| Método | Ruta | Body (JSON) | Para qué sirve |
|---|---|---|---|
| GET | `/api/admin/reportes/estudiantes-activos` | N/A | Devuelve el total de alumnos activos vs inactivos. |
| GET | `/api/admin/reportes/pagos` | N/A | Devuelve la sumatoria monetaria de ingresos reales vs deuda pendiente. |
| GET | `/api/admin/estudiantes` | N/A | Lista el directorio completo de alumnos. |
| POST | `/api/admin/estudiantes` | `{ username, email, password... }` | Registra un alumno y crea su perfil académico. |
| POST | `/api/admin/cargos` | `{ concept, amount, due_date }` | Crea un concepto de cobro y lo asigna a todos los alumnos activos. |

### 3.3 Portal del Estudiante
Los endpoints de este módulo filtran la información basándose en el **ID del token**.
- Al llamar a `/api/estudiantes/me/pagos`, la consulta SQL hace un `JOIN` entre `charges` y `payment_students` usando el `user_id` del token. Esto garantiza que un alumno **nunca** pueda ver la deuda de otro, incluso si intenta manipular la URL.

*Requieren token de sesión.*

| Método | Ruta | Para qué sirve |
|---|---|---|
| GET | `/api/estudiantes/me` | Devuelve el nombre, curso y estado del alumno logueado. |
| GET | `/api/estudiantes/me/pagos` | Cruza las tablas para devolver el historial de deudas, fechas límite y estatus de pago del alumno. |

### 3.4 Módulo de Pagos (MercadoPago)
La lógica de pagos es el corazón financiero del sistema.

**Flujo de Creación (`/api/pagos/crear`):**
- El backend construye una "Preferencia de Pago". 
- Se asigna una `X-Idempotency-Key` basada en el ID del alumno. Esto evita que, si hay un lag de red y el alumno hace doble clic, se generen dos cobros en MercadoPago.
- Se definen las **Back URLs**: Direcciones a las que MercadoPago enviará al usuario tras el pago (`success`, `failure`, `pending`).

**Flujo de Confirmación (`/api/pagos/success`):**
- Es un **Webhook**. MercadoPago envía un `payment_id`.
- El backend realiza una consulta *Server-to-Server* hacia MercadoPago para verificar que el estatus sea realmente `approved` y que el monto coincida con lo esperado.
- Tras la validación, se actualiza la tabla `payment_students`, registrando el ID de transacción externa y cambiando el estatus a `paid`.

*Rutas gestionadas de forma independiente por el enrutador `pagos_mp.py`.*

| Método | Ruta | Para qué sirve |
|---|---|---|
| POST | `/api/pagos/crear` | Genera la preferencia de pago en MercadoPago y devuelve el link seguro (`init_point`). |
| GET | `/api/pagos/success` | Recibe la confirmación de MercadoPago, valida el pago y actualiza la BD a `paid`. |
| GET | `/api/pagos/failure` | Maneja la redirección cuando un pago es rechazado. |
| GET | `/api/pagos/pending` | Maneja la redirección cuando un pago queda en proceso (Oxxo, transferencia tardía). |
| GET | `/api/pagos/historial` | Consulta la BD y devuelve el historial de pagos concretados del alumno. |

> **[INSERTA AQUÍ IMAGEN DE: image_703ab6.png - Captura enfocada exclusivamente en la sección "Pagos MercadoPago" del Swagger]**

---

## 4. Requerimientos de Base de Datos
La base de datos PostgreSQL está configurada en Azure para garantizar alta disponibilidad. El backend se comunica mediante el driver `psycopg2-binary`.

**Relaciones Clave en el Esquema:**
- **`users` 1:1 `students`**: Un usuario puede ser un estudiante con matrícula única.
- **`charges` 1:N `payment_students`**: Un cargo (ej. Colegiatura Mayo) se replica para muchos estudiantes.

| Tabla | Uso en la API | Responsabilidad Crítica |
|---|---|---|
| `roles` / `institutions` | **Lectura** | Se extraen IDs por defecto al registrar entidades. |
| `users` | **Lectura/Escritura** | Almacena el `password_hash`, validación de login e información principal. |
| `login_logs` | **Escritura** | Guarda auditorías de acceso (éxitos, fallos, IPs). |
| `students` | **Lectura/Escritura** | Almacena datos del perfil académico (matrícula, curso). |
| `charges` | **Escritura** | Almacena el concepto de deuda global. |
| `payment_students` | **Lectura/Escritura** | Tabla pivote. Asigna el monto exacto, estatus (`pending`, `paid`) y guarda el `external_reference` (ID de operación de MercadoPago). |

---

## 5. Configuración de Infraestructura y Despliegue

El despliegue en **Hugging Face Spaces** utiliza tecnología de contenedores (Docker).

**Archivo Dockerfile:**
- Utiliza una imagen base ligera de Linux (`python:3.10-slim`).
- Expone el puerto `7860`.
- Define el `WORKDIR` y copia los archivos necesarios.

**Gestión de Secretos:**
Las variables sensibles como `DB_PASSWORD` y `SECRET_KEY` no se suben al código. Se configuran en el panel de control de Hugging Face como **Secretos de Entorno**, los cuales son inyectados al contenedor en tiempo de ejecución.

> **[INSERTA AQUÍ IMAGEN DE: Captura de pantalla de la sección "Variables and secrets" en Hugging Face]**

## 6. Gestión de Errores y Glosario Técnico

- **401 Unauthorized**: El token no es válido o ha expirado.
- **403 Forbidden**: El usuario está logueado pero no tiene el rol necesario (ej. Alumno intentando entrar a reportes admin).
- **422 Unprocessable Entity**: Los datos enviados desde el frontend no cumplen con el esquema de Pydantic en `schemas.py`.
- **500 Internal Server Error**: Generalmente ocurre por una falla en la conexión con Azure o un error de lógica SQL.

---
**Documentación generada para el equipo de desarrollo EduCore.**
**Versión:** 2.0 (Detalle Expandido)



## 7. Requerimientos y Conexión con Frontend

Para que el equipo de Frontend (React/Vite) pueda consumir esta API sin errores:

### 7.1 Especificaciones de URL
La URL base debe ser inyectada **sin la diagonal final (`/`)** para evitar errores `404 Not Found` al concatenar los enrutadores.
* Correcto: `https://bitgames456-proyecto-cidium.hf.space/api`

### 7.2 Estructura del Login (OAuth2)
El protocolo OAuth2 de FastAPI exige que las credenciales de inicio de sesión se envíen en formato de formulario, no como JSON crudo. El frontend **debe** empaquetar los datos usando `URLSearchParams`.

### 7.3 Inyección del Token JWT
Recibido el JWT, el frontend debe almacenarlo y adjuntarlo en los Headers de todas las peticiones protegidas bajo el formato `Authorization: Bearer <TOKEN>`.

---

## 8. Análisis de Integración y Discrepancias

Durante el acoplamiento entre Frontend, Backend y BD, se resolvieron varios puntos clave:

### 8.1 Puntos Compatibles y Logrados
* **Modularidad Activa:** La separación en `router.py` y `pagos_mp.py` permitió desarrollar la lógica de negocio y la pasarela de pagos en paralelo sin conflictos de código.
* **Seguridad Sólida:** El middleware de FastAPI bloquea peticiones sin token, y React intercepta el error `401 Unauthorized` para expulsar al usuario al Login.

### 8.2 Discrepancias Resueltas

| Discrepancia Detectada | Impacto | Solución Implementada |
|---|---|---|
| **Idioma de las Rutas** | Frontend solicitaba `/admin/students`, Backend definía `/admin/estudiantes` (Error 404). | Se estandarizó la capa `api.js` del frontend para mapear exactamente las rutas en español expuestas por los routers. |
| **Choque de Roles (Loop)** | FastAPI devuelve `superadmin`, pero React esperaba `admin`, causando un bucle infinito ("pantalla negra"). | Se modificó `ProtectedRoute.jsx` en React para normalizar los roles y aceptar `superadmin` como perfil válido. |
| **Manejo de Perfiles Inexistentes** | Si un admin entraba al portal de alumnos, React intentaba leer un perfil inexistente y la app fallaba. | Se implementó "Optional Chaining" (`?.`) y mensajes de error amigables para evitar el colapso del sistema. |

