# Proyecto: lic_backend

## 1. Framework principal
FastAPI

## 2. Punto de entrada
`src/main.py`

## 3. Cómo se levanta localmente
`uvicorn src.main:app --reload`

## 4. Dependencias principales
* `fastapi`
* `psycopg2-binary` (PostgreSQL)
* `pydantic` y `pydantic-settings`
* `uvicorn`
* `redis`
* `bcrypt` y `python-jose`

## 5. Uso de base de datos
PostgreSQL (a través de `psycopg2`). Se conecta utilizando variables de entorno para host, bd, user o directamente a través de un `DATABASE_URL`.

## 6. Uso de Redis
Se utiliza como intermediario para comunicación asíncrona. El backend envía mensajes a colas (`document_queue` y `semantic_queue`) con los identifiers de las licitaciones (y documentos), delegando la carga pesada al worker, en lugar de bloquear su proceso.

## 7. Variables de entorno necesarias
* `DATABASE_URL` (o las separadas `DB_POSTGRES_HOST`, `DB_POSTGRES_USER`, etc.)
* `REDIS_URL` (o separar `REDIS_HOST`, `REDIS_PORT`, `REDIS_PASSWORD`, `REDIS_DB`)
* `UPLOAD_DIR`
* `CORS_ORIGINS`
* `COMPRA_AGIL_API_KEY` (y afines)

## 8. Estructura del proyecto
```text
src/
  core/           # Configuración, respuestas base
  features/       # Módulos de funcionalidad (Vertical Slices)
    auth/         # Autenticación
    dashboard/    # API para gráficas y datos
    demo/         # Rutas de pruebas
    licitaciones/ # Core: acciones CRUD, buscar, borrar, etc.
```

## 9. Endpoint principal
Rutas montadas mediante routers, notablemente:
* `/licitaciones`
* `/api`
* `/auth`
* El root `/` redirige a `/main`

## 10. ¿Tiene procesos background?
NO de forma nativa. La arquitectura actual delega el procesamiento asíncrono a sus respectivas colas en Redis para que el Worker de `lic_etl-workers` sea el encargado de procesarlas.
