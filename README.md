# Campus Online - Integración de Pagos con MercadoPago

*Proceso completo, explicación del código, requerimientos y análisis de integración entre equipos.*

Este documento describe el proceso completo de implementación del módulo de pagos, explica el código Python desarrollado, define los requerimientos para los equipos de base de datos y frontend, y analiza las discrepancias encontradas al comparar con los documentos de los demás equipos del proyecto.

<div align="center">
  <img width="647" height="422" alt="Diagrama de Flujo del Proceso de Pago" src="https://github.com/user-attachments/assets/840d8976-a29e-4fcf-b797-eec6c5fc8425" />
</div>

---

## Logística y Entorno de Pruebas

Para probar el entorno local (sandbox) sin errores, es obligatorio utilizar dos cuentas separadas:

* **Cuenta TEST-vendedor**: Utilizada para generar los cobros y obtener el Access Token.
* **Cuenta TEST-comprador**: Utilizada para simular al alumno que realiza el pago en el checkout.

---

## Documentación Completa

Para ver la explicación paso a paso, los códigos de conexión, los requerimientos exactos para las bases de datos y el análisis de integración del equipo, consulta el manual completo en el siguiente enlace:

**[Ver el Manual Técnico de Pagos](Guia-tecnica-mp.md)**
