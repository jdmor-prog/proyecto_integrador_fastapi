# 03 - Estructura del proyecto

Árbol relevante (simplificado):
```
project_name/
├── app/
│   ├── main.py                 # Inicialización de FastAPI y rutas globales
│   ├── api/
│   │   └── v1/
│   │       ├── routers.py      # Composición de APIRouter /api/v1
│   │       └── endpoints/
│   │           ├── users.py    # Rutas de usuarios
│   │           ├── items.py    # Rutas de ítems
│   │           ├── profiles.py # Rutas de perfiles (1:1)
│   │           └── categories.py # Rutas de categorías (N:N con Items)
│   ├── core/
│   │   ├── config.py           # Configuración (pydantic-settings, JWT, CORS)
│   │   ├── database.py         # SQLAlchemy Engine, SessionLocal, Base y get_db
│   │   ├── security.py         # Utilidades JWT (crear/validar tokens)
│   │   ├── auth_middleware.py  # Middleware de autorización por roles
│   │   └── routes_config.py    # Config. centralizada de acceso por ruta/prefijo
│   ├── models/
│   │   ├── user.py             # Modelo ORM User (hashed_password, role)
│   │   ├── item.py             # Modelo ORM Item (+ relación N:N con Category)
│   │   ├── profile.py          # Modelo ORM Profile (relación 1:1 con User)
│   │   └── category.py         # Modelo ORM Category (+ tabla asociación ItemCategory)
│   ├── schemas/
│   │   ├── user.py             # Schemas Pydantic v2 (UserCreate, ...)
│   │   ├── item.py             # Schemas Pydantic v2 (ItemCreate, ItemReadWithOwner + categories)
│   │   ├── profile.py          # Schemas Pydantic v2 (ProfileCreate, ...)
│   │   └── category.py         # Schemas Pydantic v2 (CategoryRead, CategoryReadWithItems)
│   ├── services/
│   │   ├── category_service.py # CRUD de categorías y consultas relacionadas
│   │   ├── user_service.py     # Lógica de negocio/DB para usuarios
│   │   ├── item_service.py     # Lógica de negocio/DB para ítems
│   │   └── profile_service.py  # Lógica de negocio/DB para perfiles 1:1
│   └── tests/
│       (sin carpeta de tests)
├── docs/                       # Documentación del proyecto
├── project.db                  # DB SQLite por defecto
└── requirements.txt
```

Capas y responsabilidades:
- `main.py`: crea `app`, registra routers, expone `/health` y `/scalar`, configura `startup`.
- `api/v1/routers.py`: agrupa endpoints bajo el prefijo `/api/v1`.
- `endpoints/*.py`: define operaciones HTTP. Usan `Depends(get_db)` para inyectar sesión.
- `models/*.py`: entidades ORM con `Base`.
- `schemas/*.py`: modelos Pydantic para entradas y salidas.
- `services/*.py`: funciones que interactúan con la DB y aplican reglas de negocio.
- `core/config.py`: configuración del proyecto y carga desde `.env`.
- `core/database.py`: crea el `engine`, `SessionLocal`, `Base` y el `get_db` dependency.

## Justificación de la arquitectura por capas

Esta organización separa claramente responsabilidades y facilita la evolución del proyecto sin romper otras partes.

- Separación de responsabilidades: cada carpeta cumple un rol único (rutas, servicios, datos, configuración). Cambios en una capa no afectan directamente a las otras.
- Acoplamiento bajo y cohesión alta: los endpoints dependen de servicios mediante interfaces claras, y los servicios operan sobre modelos y sesiones de DB bien definidas.
- Escalabilidad y mantenibilidad: es sencillo añadir nuevos módulos (p. ej., otro recurso) replicando el patrón `models/schemas/services/endpoints`.
- Reutilización: la lógica de negocio en `services` puede reutilizarse en distintos endpoints o tareas internas.
- Sustitución tecnológica: puedes cambiar la base de datos (SQLite → Postgres) modificando principalmente `core/database.py` y la configuración, sin tocar endpoints o servicios de forma masiva.
- Claridad operativa: la configuración (`core/config.py`) y el ciclo de vida de la aplicación (eventos de `startup`) están centralizados, lo que simplifica despliegues.

## Flujo típico de una petición

1. El cliente realiza una solicitud HTTP a una ruta, por ejemplo `POST /api/v1/users/`.
2. El router (`api/v1/routers.py`) dirige la petición al endpoint correspondiente (`endpoints/users.py`).
3. El endpoint valida el payload con `schemas/*` (Pydantic v2) y obtiene una sesión de DB con `Depends(get_db)`.
4. El endpoint delega en el servicio (`services/*`) la lógica de negocio y el acceso a datos.
5. El servicio interactúa con los modelos ORM (`models/*`) usando la sesión activa; crea/consulta/actualiza/borra registros.
6. La respuesta se serializa usando schemas de salida (por ejemplo `UserRead`) y se devuelve al cliente.
7. Si la ruta está protegida, el middleware valida el JWT y el rol permitido según `core/routes_config.py`.

## Decisiones específicas de este proyecto

- Versión de API: se usa un `APIRouter` con prefijo `/api/v1`, lo que permite versionar rutas y mantener compatibilidad futura.
- Pydantic v2: se emplea `ConfigDict(from_attributes=True)` en los schemas de lectura para construir respuestas directamente desde objetos ORM.
- Sesiones por petición: `get_db()` abre una sesión por request y la cierra de forma fiable, evitando fugas de conexión.
- Documentación: la UI de Scalar consume el `openapi_url` generado por FastAPI y se expone en `GET /scalar`.
- Creación de tablas en `startup`: útil en desarrollo; en producción es recomendable usar migraciones con Alembic.
 - Seguridad: JWT HS256 con expiración configurable. Autorización por roles (`admin`, `user`, `guest`) aplicada mediante middleware y configuración centralizada de rutas.