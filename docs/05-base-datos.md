# 05 - Base de datos y sesiones

La capa de base de datos usa `SQLAlchemy`.

Archivo: `app/core/database.py`
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine = create_engine(settings.database_url, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Conceptos clave:
- `engine`: conexión a la base de datos. `pool_pre_ping=True` evita conexiones muertas.
- `SessionLocal`: fábrica de sesiones. `autocommit=False` y `autoflush=False` dan control explícito.
- `Base`: clase base para modelos ORM (`User`, `Item`).
- `get_db()`: dependencia de FastAPI que abre/cierra una sesión por petición.

## Ciclo de vida de la sesión
- En cada request, `Depends(get_db)` inyecta una sesión abierta.
- Los servicios hacen `db.add()`, `db.commit()`, `db.refresh()` según corresponda.
- Al finalizar, la sesión se cierra en el `finally` del `get_db()`.

## Creación del esquema
- En `startup`, si `AUTO_CREATE_TABLES=true`, se ejecuta `Base.metadata.create_all(bind=engine)`.
- En producción, considera usar migraciones con `Alembic` en lugar de crear tablas automáticamente.

## SQLite y concurrencia
- SQLite no soporta alta concurrencia. Para desarrollo está bien.
- Evita ejecutar dos servidores a la vez leyendo/escribiendo la misma DB.

## Datos de prueba (Seeds)

Para poblar la base con usuarios de prueba, utiliza el script:

```bash
python scripts/seed_users.py
```

Si cambiaste el esquema (por ejemplo añadiste columnas nuevas al modelo `User`), usa la opción de reseteo para recrear tablas antes de sembrar:

```bash
python scripts/seed_users.py --reset
```

Alternativa recomendada para evitar problemas de import en algunos entornos:

```bash
python -m scripts.seed_users --reset
```

Vaciar la base sin sembrar (tablas vacías tras recrear esquema):

```bash
python -m scripts.seed_users --empty
```

Advertencias:
- `--reset` ejecuta `Base.metadata.drop_all()` seguido de `create_all()`, lo que borra tablas y datos.
- En SQLite, esto afecta al archivo `project.db`. Haz respaldo si necesitas conservar datos.