# 🎓 EduCore MVP: Sistema Integral de Gestión Académica y Cobranza

[![Python](https://img.shields.io/badge/Python-3.10-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-v0.100+-05998b.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://www.docker.com/)
[![Azure](https://img.shields.io/badge/Microsoft_Azure-PostgreSQL-0089d6.svg)](https://azure.microsoft.com/)
[![HuggingFace](https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Spaces-yellow)](https://huggingface.co/spaces)

**EduCore** es una solución Full-Stack diseñada para la modernización de servicios escolares. Este repositorio contiene el **Core Backend**, una API REST de alto rendimiento que orquesta la autenticación, la gestión de matrícula, la reportería administrativa y una pasarela de pagos automatizada.

---

## 🚀 Vista Rápida del Sistema

* **API en Vivo:** [Hugging Face Space](https://bitgames456-proyecto-cidium.hf.space/docs)
* **Base de Datos:** PostgreSQL en Microsoft Azure.
* **Seguridad:** OAuth2 con JWT y cifrado Bcrypt.
* **Integración Financiera:** MercadoPago Checkout Pro (Sandbox).

---

## 🛠️ Stack Tecnológico

El backend fue construido bajo estándares de ingeniería de software modernos para asegurar rapidez y seguridad:

* **FastAPI:** Framework asíncrono que permite manejar múltiples peticiones simultáneas (ideal para procesos de pago).
* **Pydantic:** Validación estricta de esquemas de datos.
* **SQLAlchemy / Psycopg2:** Comunicación eficiente con la capa de persistencia en Azure.
* **Docker:** Contenerización para un despliegue agnóstico y escalable.

---

## 🏗️ Arquitectura del Backend

El sistema se divide en **Routers Independientes** para facilitar el mantenimiento y la escalabilidad del código:

1.  **Auth Router:** Gestión de sesiones, auditoría de accesos (`login_logs`) y seguridad JWT.
2.  **Admin Router:** Generación de reportes de inteligencia de negocio, gestión de matrícula y cargos financieros masivos.
3.  **Student Router:** Portal privado para el alumno donde consulta sus deudas y perfil académico.
4.  **Payment Router:** Integración directa con MercadoPago para la automatización de cobranza.

<div align="center">
  
</div>

---

## 📊 Módulos Principales y Endpoints

### 🔐 Seguridad y Acceso
Implementa un flujo de **OAuth2**. Al iniciar sesión, el servidor genera un Token JWT que el frontend debe persistir y enviar en cada petición protegida.
* `POST /api/auth/login`: Validación de credenciales y entrega de Token.
* `GET /health`: Monitor de salud del servidor en tiempo real.

### 🏛️ Dashboard Administrativo
Diseñado para la toma de decisiones basada en datos reales de Azure.
* `GET /api/admin/reportes/estudiantes-activos`: Estadísticas de retención.
* `GET /api/admin/reportes/pagos`: Visibilidad de ingresos vs cartera vencida.
* `POST /api/admin/cargos`: Automatización de deudas escolares.

### 💳 Pasarela de Pagos (MercadoPago)
Un flujo automatizado que reduce la carga operativa de cobranza manual.
* `POST /api/pagos/crear`: Genera una preferencia de pago segura.
* `GET /api/pagos/success`: Webhook que confirma y liquida deudas en la base de datos automáticamente.

---

## 📦 Instalación y Despliegue Local

Si deseas correr este proyecto en tu entorno local (Kubuntu/Linux recomendado):

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/Gamesrack565/Proyecto---Cidium-Security-University.git](https://github.com/Gamesrack565/Proyecto---Cidium-Security-University.git)
   cd Proyecto---Cidium-Security-University
