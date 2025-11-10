# Project Name

Estructura base de un proyecto FastAPI con rutas versión `v1`, modelos y esquemas mínimos.

## Requisitos

- Python 3.10+
- Pip/venv

## Instalación

```bash
cd project_name
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Ejecutar

```bash
uvicorn app.main:app --reload
```

Visita `http://127.0.0.1:8000/health` para verificar estado.

API base:
- `GET /api/v1/users/` y `POST /api/v1/users/`
- `GET /api/v1/items/` y `POST /api/v1/items/`

> Nota: Los endpoints usan listas en memoria para simplificar. La configuración de base de datos está preparada en `app/core/database.py` y `app/core/config.py`.



## Configuración de Base de Datos

Por defecto se usa SQLite (`sqlite:///./project.db`). Para usar PostgreSQL, configura `DATABASE_URL` en `.env`:

```env
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/mi_base
```

Ejemplos:
- SQLite local: `DATABASE_URL=sqlite:///./project.db`
- PostgreSQL local con Docker: `postgresql+psycopg://postgres:postgres@localhost:5432/appdb`

> En entornos productivos se recomienda usar migraciones (Alembic). Aquí las tablas se crean automáticamente al iniciar si `auto_create_tables=true`.

## Relaciones ORM

El proyecto usa relaciones bidireccionales entre `User` e `Item`:

- `User.items` tiene `cascade="all, delete-orphan"` y `passive_deletes=True`.
- `Item.owner` se enlaza con `ForeignKey("users.id", ondelete="CASCADE")`.

Los servicios aplican `selectinload` para cargar relaciones eficientemente en listados y detalles, evitando problemas de N+1 consultas.

Al crear/actualizar ítems se valida que el `owner` exista y se vincula mediante la relación (`item.owner = user`).

## Despliegue en Render.com (Docker)

Este repositorio incluye configuración para desplegar en Render usando Docker.

- `Dockerfile`: arranca `uvicorn app.main:app` en `0.0.0.0:$PORT`.
- `.dockerignore`: excluye venv, caches y secretos del contexto.
- `render.yaml`: blueprint opcional para crear el servicio con un clic.
- Guía detallada: ver `docs/14-deploy-render.md`.

Pasos rápidos:
- Conecta el repo en Render → “New” → “Web Service”.
- Environment: `Docker`. Health Check Path: `/health`.
- Configura `DATABASE_URL` si necesitas persistencia (PostgreSQL recomendado). Por defecto usa SQLite efímero.