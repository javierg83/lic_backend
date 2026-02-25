# Mejoras Futuras y Deuda Técnica (Backend Project)

## Robustez ETL
- [ ] **Manejo de IDs Nulos en ProcessDocumentNode**: Actualmente, si `licitacion_internal_id` o `archivo_internal_id` son nulos, el archivo se procesa pero NO se agrega a la lista para extracción semántica.
    - *Solución*: Implementar lógica de fallback para usar solo el nombre del archivo (como hace `SaveService`) y agregarlo a la lista `processed_files`.
- [ ] **Reintento de Errores**: Implementar mecanismo de reintento automático para fallos transitorios (conexión DB/Redis).

## Centralización
- [ ] **Librería Compartida**: Mover `states.py` y otras constantes a una librería pip instalable o submódulo git para evitar duplicación de código entre microservicios.

## Funcionalidades Core
- [ ] **Borrado Lógico de Licitaciones**: Implementar borrado lógico (e.g., campo `deleted_at` o `is_deleted`). El borrado **no debe ser a nivel de base de datos** (DELETE SQL); el registro debe mantenerse en la DB por integridad histórica, pero debe modificarse la lógica en el backend y frontend para que no sea visible en los formularios, listados ni detalles respectivos.
