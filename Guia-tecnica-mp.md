# Manual Técnico: Integración de Pagos con MercadoPago

## Índice
* [1. Proceso completo de implementación](#1-proceso-completo-de-implementación)
* [2. Explicación del código Python](#2-explicación-del-código-python)
* [3. Requerimientos de Base de Datos](#3-requerimientos-de-base-de-datos)
* [4. Requerimientos de Frontend](#4-requerimientos-de-frontend)
* [5. Análisis de integración con los demás equipos](#5-análisis-de-integración-con-los-demás-equipos)

---

## 1. Proceso completo de implementación

Para realizar la demo de pagos con MercadoPago se siguieron los siguientes pasos:

### 1.1 Creación de la cuenta en MercadoPago Developers
Se accede al portal de desarrolladores y se creó la aplicación Campus Online:

|Dato| Valor|
|----|------|
|Nombre de la aplicacion|Campus online|
|Numero de la aplicacion| 4552392274773713|
|Tipo de integracion| Checkout Pro|
|Pais |Mexico (MXN)|

### 1.2 Creación de dos cuentas de prueba
**Regla de MercadoPago en sandbox:**
Si intentamos pagar con la misma cuenta con la que se genera el cobro, MercadoPago mostrará el error: *"Una de las partes con la que intentas hacer el pago es de prueba"*. Por eso es que necesitamos crear dos cuentas TEST separadas.

|Cuenta | Tipo | Saldo Ficticio | Para que se usa|
|-----|----|----|----|
|Test-Vendedor| Vendedor | $1000 MXN | Genera los cobros. Su Access Token se usa en el código Python.|
|Test-Comprador| Comprador | $5000 MXN | Simula al alumno que realiza el pago en el checkout.|

### 1.3 Creación de cuentas de prueba paso a paso

1. **Entrar a la aplicación:** Nos dirigimos al enlace `mercadopago.com.mx/developers`, hacemos clic en "Tus integraciones" y seleccionamos Campus Online.
<img width="974" height="312" alt="1" src="https://github.com/user-attachments/assets/16ce7694-6b4d-4803-a536-1089facf2227" />

2. **Crear cuenta Vendedor:** En la pestaña "Cuentas de prueba", hacemos clic en "Crear cuenta". Tipo: Vendedor, saldo: $1,000. Guardar usuario y contraseña generados.
<img width="315" height="412" alt="2" src="https://github.com/user-attachments/assets/443e7de3-e1d3-49ec-a408-dac88e1814b2" />
<img width="976" height="319" alt="3" src="https://github.com/user-attachments/assets/af167163-6a93-4f8c-a17c-589c7eeb34e3" />

3. **Crear cuenta Comprador:** Repetimos el proceso con la cuenta de Tipo: Comprador, y le agregamos un saldo: $5,000.
<img width="653" height="410" alt="4" src="https://github.com/user-attachments/assets/283f6017-e419-4263-b05a-97eeb4006cd3" />
<img width="812" height="267" alt="5" src="https://github.com/user-attachments/assets/4608956f-87e1-41a3-929b-b5d6cd697a18" />

4. **Obtener Access Token del vendedor:** Iniciamos sesión en la ruta developer de la página de Mercado Pago con la cuenta TEST-vendedor en una ventana incógnita. Nos dirigimos a la pestaña de "Credenciales de prueba" y copiamos el token Access Token TEST.

<img width="822" height="415" alt="6" src="https://github.com/user-attachments/assets/b216d982-1d9a-44fe-83f6-19a65db0a208" />

### 1.4 Cómo se realizó el pago de prueba
**1.4.1 Ejecutamos nuestro script de Python**
Para ello usamos el siguiente comando:
```bash
uvicorn fastAPI:app --reload
```
<img width="976" height="194" alt="7" src="https://github.com/user-attachments/assets/b1a8e02b-d953-4697-ab37-6e782265a75b" />

**1.4.2 Generar link de pago**
Abrimos el `http://localhost:8000/docs`, nos dirigimos a la opción de `POST /api/pagos/crear`. Entonces la API responderá con un `sandbox_init_point`, tal y como se aprecia en las imágenes de abajo.
<img width="952" height="305" alt="8" src="https://github.com/user-attachments/assets/1046f4f7-3ce9-4627-b99b-adde09b82ab3" />
<img width="962" height="335" alt="9" src="https://github.com/user-attachments/assets/ed011f3b-e4ce-4492-9ebe-5adf62d9ee98" />

**1.4.3 Abrir ventana incógnita o un nuevo navegador**
Para no interferir con la sesión real abrimos un nuevo navegador o una ventana incógnita con `Ctrl+Shift`. En este caso yo abro el navegador vivaldi y pegamos el link del sandbox.

<img width="973" height="281" alt="10" src="https://github.com/user-attachments/assets/54008664-e42a-4c48-b536-1052946a89b0" />

**1.4.4 Iniciar sesión con cuenta comprador TEST-**
El checkout solicita login para ello por defecto se usan las credenciales de la cuenta TEST-comprador, lo que habilitará el botón Pagar.

**1.4.5 Completar el pago**
Con sesión del comprador activa, el botón Pagar se habilita, entonces hacemos clic para que MercadoPago procese la transacción.

En este ejemplo para pagar usamos la opción de "Dinero en Mercado Pago".
<img width="807" height="415" alt="11" src="https://github.com/user-attachments/assets/8bbab966-9a3f-4420-b1af-d719fd4db82e" />


**1.4.6 Confirmación**
MercadoPago nos mostrará el siguiente mensaje: *"Listo! Tu pago ya se acreditó. Operación #155522875569, $1,500 MXN."*
<img width="811" height="342" alt="12" src="https://github.com/user-attachments/assets/1b4fdd55-80e1-44ee-b1b5-91753ceaa31e" />

**1.4.7 Revisamos el comprobante**
Hacemos click en el botón de "Ver comprobante" como se aprecia en la siguiente captura de pantalla.
<img width="582" height="454" alt="13" src="https://github.com/user-attachments/assets/e5d0fbf4-4108-42a4-9a25-440a27d3e4b7" />

¡Listo! De esta manera comprobamos que nuestra demo local funciona con éxito.
---
# 2. Explicación del código Python

## 2.1 Importaciones y configuración inicial
<img width="683" height="101" alt="14" src="https://github.com/user-attachments/assets/15114b99-5bc1-470a-95a9-295d694ddd89" />

- **`FastAPI`**: Framework que convierte funciones Python en endpoints HTTP.
- **`requests`**: Librería para hacer peticiones HTTP hacia la API de MercadoPago.
- **`ACCESS_TOKEN`**: Llave de autenticación. Identifica la cuenta vendedor ante MercadoPago en cada petición.

## 2.2 Endpoint `POST /api/pagos/crear`

### Parte A – Headers
<img width="620" height="120" alt="15" src="https://github.com/user-attachments/assets/b5a9e0cc-148e-4e50-931b-dc24dbde1619" />

- **`Authorization`**: Autentica la petición. Sin este header MercadoPago responde `401`.
- **`X-Idempotency-Key`**: Evita cobros duplicados si el alumno hace doble clic.

### Parte B - Datos del pago
<img width="556" height="181" alt="16" src="https://github.com/user-attachments/assets/2e35cbbc-c643-4503-b84f-694ac4f773ba" />

El `title` es lo que ve el alumno en el checkout. Por otro lado, el `payer.email` en producción debe venir del alumno logueado en el sistema.

### Parte C - Back URLs

<img width="588" height="120" alt="17" src="https://github.com/user-attachments/assets/6f8737e2-31cb-4624-8b49-778dc605364d" />

En producción estas URLs deben ser públicas. Es importante mencionar que la página de MercadoPago las llama desde sus servidores tras el pago.

### Parte D - Respuesta y manejo de errores
<img width="781" height="222" alt="18" src="https://github.com/user-attachments/assets/b93fba55-8a51-453b-a43e-f174b66eb696" />

- **`status_code 201`**: MercadoPago regresa `201` cuando el checkout se creó correctamente.
- **`init_point`**: URL del checkout real para producción. Es la URL generada dinámicamente por la API de Mercado Pago que contiene toda la configuración de la compra (monto, descripción y datos del alumno). En nuestro entorno de producción real, el Front-End utiliza este enlace para redirigir al usuario a una interfaz segura donde se procesan transacciones reales.

## 2.3 Resumen de endpoints

|Metodo|Ruta|Quien lo llama|Para que sirve|
|-|-|-|-|
|GET|/|Cualquiera|Verifica que el servidor está corriendo|
|POST|/api/pagos/crear|Frontend|Genera el link de pago en MercadoPago|
|GET|/success|MercadoPago|Recibe confirmación de pago aprobado|
|GET|/failure|MercadoPago|Recibe notificación de pago rechazado|
|GET|/pending|MercadoPago|Recibe notificación de pago pendiente|
|GET|/api/alumnos/me/pagos|FrontEnd|Regresa el historial de pagos del alumno|

## 2.4 Endpoint nuevo `GET /api/alumnos/me/pagos`

Este endpoint se agregó para estar alineados con el documento Endpoints, porque este permite al frontend mostrar el historial de pagos de un alumno.

---

## Estrategia: dos versiones en el mismo archivo

La versión simulada funciona ahora sin base de datos, permitiendo al equipo de frontend conectarse y probar. La versión real es comentada y se activa cuando el equipo de BD entregue la conexión.

- **Versión simulada**: Funciona ahora sin BD.
<img width="855" height="289" alt="19" src="https://github.com/user-attachments/assets/4dcea993-6b3b-4182-83fa-06a9652a56b9" />

- **Versión real**: Se activará cuando haya conexión a BD.
<img width="942" height="59" alt="20" src="https://github.com/user-attachments/assets/6c5c35db-68c6-475f-b4e1-fb89118cf43e" />
<img width="943" height="60" alt="21" src="https://github.com/user-attachments/assets/59a5bb06-24ba-4190-9ce8-b7bee77cdf18" />

### Respuesta que recibe el frontend

El formato coincide exactamente con lo definido en el archivo `Endpoints.docx` del otro equipo:

<img width="942" height="164" alt="22" src="https://github.com/user-attachments/assets/f541450c-016b-47f0-a973-01dfe817d9ec" />

# 3. Requerimientos de Base de Datos

## 3.1 Tabla existente: `PAYMENT_STUDENTS`
Esta tabla ya existe en el diagrama ER. A continuación se muestran todos sus campos y cuáles son los que usa el módulo de pagos:

|Campo|Tipo|Uso por Pagos|Descripcion|
|-|-|-|-|
|id|STRING|No|Identificador único del registro.|
|payment_id|STRING FK| No|Referencia al concepto de pago en tabla PAYMENTS.|
|student_id|STRING FK|No|Referencia al alumno en tabla STUDENTS.|
|assigned_amount|DECIMAL|No|Monto asignado al alumno para ese pago.|
|paid_amount|DECIMAL| Escribir | Monto que MercadoPago confirmó como cobrado.|
|paid_at|DATETIME | Escribir | Fecha y hora exacta del pago confirmado.|
|payment_method|STRING | Escribir | Se guarda 'mercadopago' al confirmar el pago.|
|external_reference|STRING|Escribir|Aquí se guarda el payment_id que genera MercadoPago.|
|status|STRING|Escribir|Se cambia a 'paid' cuando el pago es aprobado.|

## 3.2 Qué debe hacer el equipo de base de datos
Lo que se necesita del equipo de BD es:
- Confirmar que el campo `external_reference` acepta el formato del `payment_id` de MercadoPago (string de hasta 100 caracteres).
- Confirmar que el campo `payment_method` acepta el valor `'mercadopago'`.
- Confirmar que el campo `status` acepta los valores: `'pending'`, `'paid'`, `'rejected'`.
- Exponer un procedimiento o permitir el `UPDATE` desde la API cuando un pago es aprobado.

## 3.3 Consultas que usará la API
- **Verificar si un pago ya fue procesado** (evitar duplicados).

<img width="941" height="41" alt="23" src="https://github.com/user-attachments/assets/2b915571-1d7b-4c32-aee5-7cee254c62ed" />

- **Registrar el pago aprobado.**

<img width="750" height="164" alt="24" src="https://github.com/user-attachments/assets/a230df42-74e9-4da0-b9bc-4c6a0d721842" />

- **Verificar si un alumno tiene pago activo.**

<img width="637" height="104" alt="25" src="https://github.com/user-attachments/assets/16c74257-d97e-4b71-bf08-1216995469e9" />

- **Historial de pagos del alumno** (para el endpoint `GET /api/alumnos/me/pagos`).
<img width="660" height="102" alt="26" src="https://github.com/user-attachments/assets/3b49f97a-ecf7-4603-9209-cc4cd1404953" />

---

# 4. Requerimientos de Frontend

## 4.1 Botón de pago y llamada a la API
<img width="949" height="221" alt="27" src="https://github.com/user-attachments/assets/172cea4e-4728-4bcc-a532-cba73adb8829" />

## 4.2 Páginas de resultado requeridas
|Ruta|Caso|Que debe mostrar|
|-|-|-|
|/success|Pago aprobado|Mensaje de confirmación, número de operación y acceso activado.|
|/failure|Pago rechazado|Mensaje de error y botón para intentar de nuevo.|
|/pending|Pago pendiente|Aviso de que el pago está en proceso.|
---

# 5. Análisis de integración con los demás equipos
Se revisaron los documentos entregados por los otros equipos del proyecto: el diagrama Entidad-Relación, el documento de endpoints y los códigos de respuesta. A continuación se presentan los puntos de compatibilidad y las discrepancias que deben resolverse antes de la integración final.

### Documentos revisados
- **diagrama-E-R.pdf** — Esquema relacional de la base de datos (Equipo Platform)
- **Endpoints.docx** — Definición de rutas y respuestas de la API
- **Codigos_.docx** — Ejemplos de respuestas HTTP
- **Documento_guia_proyecto_integrador_EduCore_MVP.docx** — Guía general del proyecto

## 5.1 Puntos compatibles
Los siguientes elementos ya están alineados entre lo que desarrollamos y lo que definieron los demás equipos:

- **Compatible 1 — Campo `external_reference` en `PAYMENT_STUDENTS`**
  El diagrama ER ya incluye el campo `external_reference` en la tabla `PAYMENT_STUDENTS`. Este campo es exactamente donde debe guardarse el `payment_id` que genera MercadoPago al aprobar una transacción. No se necesita ningún cambio en el esquema para soportar la integración.

- **Compatible 2 — Monto de la colegiatura**
  El documento guía define la colegiatura en $1,500 y el código implementado usa ese mismo valor. Ambos coinciden.

- **Compatible 3 — Módulos de autenticación y reportería**
  Los endpoints de login, logout, `/api/auth/me`, `/api/administrador/reporteactivos` y `/api/administrador/reportepagos` no tienen conflicto con el módulo de pagos. Pueden desarrollarse en paralelo sin dependencias.

- **Compatible 4 — Historial de pagos del alumno**
  El endpoint `GET /api/alumnos/me/pagos` definido en `Endpoints.docx` se apoya en las tablas `PAYMENT_STUDENTS` y `PAYMENTS` del diagrama ER, que ya incluyen los campos necesarios para mostrar fecha, descripción y monto de cada pago.

## 5.2 Discrepancias que deben resolverse

### Discrepancia 1 — Stripe vs MercadoPago
- **Problema:** El documento guía del proyecto indica explícitamente: "Se usa STRIPE para procesar pagos". Sin embargo, la implementación desarrollada usa MercadoPago. Ambos son pasarelas de pago válidas para sandbox, pero tienen flujos técnicos distintos. Esta decisión afecta el nombre de los campos, la forma del request y las URLs de retorno.
- **Acción recomendada:** Confirmar con Alan que la pasarela de pagos será con la API Mercado Pago. Si se aprueba MercadoPago, actualizar el documento guía. Si se requiere Stripe, el código necesita rehacerse con el SDK de Stripe.

### Discrepancia 2 — Nombre del endpoint no coincide
- **Problema:** El documento `Endpoints.docx` define la ruta como `POST /api/pagos/procesar`. El código implementado usa `POST /api/pagos/crear`. El frontend y el backend deben usar exactamente el mismo nombre o la conexión fallará.
- **Acción recomendada:** Acordar con el equipo de endpoints y el equipo de frontend cuál nombre usar. Se recomienda `/api/pagos/crear` porque describe mejor la acción (crear una preferencia de pago), pero cualquier nombre funciona si todos lo usan igual.

### Discrepancia 3 — El request body es incompatible con MercadoPago
- **Problema:** El documento `Endpoints.docx` define el body de `POST /api/pagos/procesar` como: `{ payment_id, card_number, exp_date, cvc, country }`. Estos son campos de tarjeta que corresponden al flujo de Stripe. Sin embargo, con MercadoPago, el alumno ingresa los datos de tarjeta directamente en el checkout de MercadoPago — nunca los envía a nuestro servidor. El request correcto para MercadoPago es: `{ email, monto, descripcion }`.
- **Acción recomendada:** Debemos actualizar el documento de endpoints con el request body correcto para MercadoPago. El equipo de frontend debe enviar email, monto y descripción, no datos de tarjeta.

### Discrepancia 4 — Faltan los endpoints de retorno en la documentación
- **Problema:** Los endpoints `GET /success`, `GET /failure` y `GET /pending` no aparecen en el documento `Endpoints.docx`. MercadoPago los necesita para redirigir al alumno después del pago. Sin estas rutas documentadas, el equipo de frontend no sabrá qué páginas debe crear.
- **Acción recomendada:** Agregar estos tres endpoints al documento de endpoints del proyecto con sus rutas, quién los llama (MercadoPago) y qué parámetros reciben (`payment_id`, `status` en la URL).

### Discrepancia 5 — La tabla pagos nueva vs usar `PAYMENT_STUDENTS` existente
- **Problema:** El documento de requerimientos que generamos pide crear una tabla nueva llamada pagos. Sin embargo, el diagrama ER del equipo Platform ya tiene la tabla `PAYMENT_STUDENTS` con los campos necesarios: `external_reference` (para el `payment_id` de MercadoPago), `paid_amount`, `paid_at`, `payment_method` y `status`.
- **Acción recomendada:** No crear una tabla nueva. En lugar de eso, usar la tabla `PAYMENT_STUDENTS` ya definida. Al confirmar un pago aprobado, guardar el `payment_id` de MercadoPago en el campo `external_reference` y actualizar `paid_amount`, `paid_at`, `payment_method` y `status` en el registro correspondiente al alumno.

## 5.3 Cómo debe quedar el flujo con la BD real
Usando la estructura de tablas del diagrama ER, el flujo correcto al recibir un pago aprobado es:

1. **MercadoPago llama a `/success` con `payment_id`:** La API recibe el `payment_id` en los parámetros de la URL.
2. **Verificar con MercadoPago que el pago es real:** `GET https://api.mercadopago.com/v1/payments/{payment_id}` — confirmar que `status == approved`.
3. **Buscar el registro en `PAYMENT_STUDENTS`:** Identificar cuál es el cargo pendiente del alumno usando su `student_id` y el `payment_id` de `PAYMENTS`.
4. **Actualizar `PAYMENT_STUDENTS`:** Llenar los campos: `external_reference` = `payment_id` de MP, `paid_amount` = monto cobrado, `paid_at` = fecha actual, `payment_method` = `mercadopago`, `status` = `paid`.

<img width="637" height="222" alt="28" src="https://github.com/user-attachments/assets/e314fcf3-1a9e-44dc-9c86-f79d0aaabf19" />

## 5.4 Tabla resumen de discrepancias
|No.|Discrepancia|Impacto|Estado|Accion|
|-|-|-|-|-|
|1|Stripe vs MercadoPago|Alto — afecta toda la integración|Sin resolver|Confirmar con maestro|
|2|Nombre del endpoint|Alto — frontend no conecta|Sin resolver|Acordar nombre único|
|3|Request body incompatible|Alto — datos incorrectos|Sin resolver|Actualizar Endpoints.docx|
|4|Faltan endpoints de retorno|Medio — frontend no sabe que paginas crear|Sin resolver|Agregar a Endpoints.docx|

---
 
# 6. Resumen de requerimientos por equipo

| Área | Qué necesita entregar | Prioridad |
|---|---|---|
| Base de datos | Confirmar uso de PAYMENT_STUDENTS para registrar pagos MP | Alta |
| Base de datos | Exponer campo external_reference para guardar payment_id | Alta |
| Endpoints | Actualizar nombre: /api/pagos/crear | Alta |
| Endpoints | Corregir request body (email, monto, descripción) | Alta |
| Endpoints | Agregar /success, /failure y /pending | Alta |
| Frontend | Botón que llame a POST /api/pagos/crear | Alta |
| Frontend | Enviar email, monto y descripción (sin datos de tarjeta) | Alta |
| Frontend | Redirigir al alumno al init_point recibido | Alta |
| Frontend | Crear páginas /success, /failure y /pending | Alta |
| Frontend | Confirmar si usar Stripe o MercadoPago con Alan | Alta |
---
