# 04 - Configuración y variables de entorno

El proyecto usa `pydantic-settings` para cargar configuración desde variables de entorno y un archivo `.env`.

Archivo: `app/core/config.py`
```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Project Name API"
    database_url: str = "sqlite:///./project.db"
    auto_create_tables: bool = True

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
```

Claves disponibles:
- `APP_NAME` (`app_name`): nombre del proyecto que aparece en `FastAPI(title=...)`.
- `DATABASE_URL` (`database_url`): URL de la base de datos (por defecto SQLite local).
- `AUTO_CREATE_TABLES` (`auto_create_tables`): si `True`, crea tablas en `startup`.

## Configuración de CORS

Se gestiona mediante `CORSMiddleware` y variables en `.env` (formato JSON):

- `CORS_ALLOW_ORIGINS` (`cors_allow_origins`): lista de orígenes permitidos en JSON.
  - Ejemplo: `["http://localhost:3000","http://127.0.0.1:5173"]`.
- `CORS_ALLOW_METHODS` (`cors_allow_methods`): métodos permitidos (JSON array).
- `CORS_ALLOW_HEADERS` (`cors_allow_headers`): encabezados permitidos (JSON array).
- `CORS_ALLOW_CREDENTIALS` (`cors_allow_credentials`): si se permiten credenciales.

Archivo: `app/main.py`
```python
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)
```

Nota: si `allow_credentials=True`, los navegadores requieren orígenes explícitos (no `*`).

## Ejemplo de `.env`
```
APP_NAME="Project Name API"
DATABASE_URL="sqlite:///./project.db"
AUTO_CREATE_TABLES=true

# CORS
CORS_ALLOW_ORIGINS=["http://localhost:3000","http://127.0.0.1:5173"]
CORS_ALLOW_METHODS=["GET","POST","PUT","PATCH","DELETE","OPTIONS"]
CORS_ALLOW_HEADERS=["*"]
CORS_ALLOW_CREDENTIALS=true
```

## Cambiar a otra base de datos
- Postgres: `postgresql+psycopg2://user:pass@localhost:5432/dbname`
- MySQL: `mysql+pymysql://user:pass@localhost:3306/dbname`

Si no es SQLite, en `database.py` se eliminará `check_same_thread=False` automáticamente.

## Inicio de la app y creación de tablas

Archivo: `app/main.py`
```python
@app.on_event("startup")
def on_startup():
    if settings.auto_create_tables:
        Base.metadata.create_all(bind=engine)
```

Esto crea las tablas si no existen cuando arranca el servidor y `AUTO_CREATE_TABLES=true`.