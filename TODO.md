# Mejoras Futuras y Deuda Técnica (Backend Project)

## Robustez ETL
- [ ] **Manejo de IDs Nulos en ProcessDocumentNode**: Actualmente, si `licitacion_internal_id` o `archivo_internal_id` son nulos, el archivo se procesa pero NO se agrega a la lista para extracción semántica.
    - *Solución*: Implementar lógica de fallback para usar solo el nombre del archivo (como hace `SaveService`) y agregarlo a la lista `processed_files`.
- [ ] **Reintento de Errores**: Implementar mecanismo de reintento automático para fallos transitorios (conexión DB/Redis).

## Centralización
- [ ] **Librería Compartida**: Mover `states.py` y otras constantes a una librería pip instalable o submódulo git para evitar duplicación de código entre microservicios.

## Funcionalidades Core
- [ ] **Borrado Lógico de Licitaciones**: Implementar borrado lógico (e.g., campo `deleted_at` o `is_deleted`). El borrado **no debe ser a nivel de base de datos** (DELETE SQL); el registro debe mantenerse en la DB por integridad histórica, pero debe modificarse la lógica en el backend y frontend para que no sea visible en los formularios, listados ni detalles respectivos.
13: 
14: ## Performance y UX
15: - [ ] **Asincronía en Importación Compra Ágil**: Mover la lógica de `CompraAgilService.import_compra_agil` a una tarea de fondo.
16:     - *Problema*: Actualmente el proceso de Selenium (`_capture_web_screenshot`) y la descarga de adjuntos son síncronos y bloquean el hilo de FastAPI/Uvicorn, impidiendo navegar por otras secciones del sistema mientras se importa.
17:     - *Solución*: El controlador debe retornar un `202 Accepted` inmediatamente y procesar el scraping y las descargas en segundo plano (vía `fastapi.BackgroundTasks` o el Worker de Redis).
18: - [ ] **Optimización de Selenium**: Asegurar que las instancias de WebDriver se cierren correctamente y considerar el uso de un pool o una solución más ligera si la carga aumenta.

## Calidad de Datos (Licitaciones)
- [ ] **[PENDIENTE]** Implementar detalle de distribución de entregas por ítem (Licitaciones Públicas).
