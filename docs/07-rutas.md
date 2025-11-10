# 07 - Rutas y Routers (FastAPI)

## Composición de routers

`app/api/v1/routers.py`
```python
from fastapi import APIRouter
from .endpoints import users, items, profiles, categories

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users.router)
api_router.include_router(items.router)
api_router.include_router(auth.router)
api_router.include_router(profiles.router)
api_router.include_router(categories.router)
```

- Se crea un `APIRouter` raíz con prefijo `/api/v1`.
- Se incluyen los routers específicos de `users`, `items`, `profiles` y `categories`.

En `app/main.py` se registra:
```python
app.include_router(api_router)
```

## Endpoints de usuarios

`app/api/v1/endpoints/users.py`
```python
router = APIRouter(prefix="/users", tags=["users"])  # prefijo bajo /api/v1

@router.get("/", response_model=list[UserRead])
@router.post("/", response_model=UserRead)
@router.get("/{user_id}", response_model=UserRead)
@router.put("/{user_id}", response_model=UserRead)
@router.patch("/{user_id}", response_model=UserRead)  # actualización parcial
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
```

Rutas completas y ejemplos:
- `GET /api/v1/users/`
  - Lista usuarios. Query params: `skip`, `limit`, `search`.
- `POST /api/v1/users/`
  - Crea usuario.
  - Body:
    ```json
    {"name": "Alice", "email": "alice@example.com"}
    ```
- `GET /api/v1/users/{user_id}`
  - Devuelve un usuario por id.
- `PUT /api/v1/users/{user_id}`
  - Actualiza parcialmente. Body ej.:
    ```json
    {"name": "Alice Updated"}
    ```
- `PATCH /api/v1/users/{user_id}`
  - Actualización parcial de campos puntuales (igual que PUT, pero semánticamente parcial).
- `DELETE /api/v1/users/{user_id}`
  - Borra usuario. Respuesta `204`.

## Endpoints de ítems

`app/api/v1/endpoints/items.py`
```python
router = APIRouter(prefix="/items", tags=["items"])  # prefijo bajo /api/v1

@router.get("/", response_model=list[ItemReadWithOwner])
@router.post("/", response_model=ItemReadWithOwner)
@router.get("/{item_id}", response_model=ItemReadWithOwner)
@router.put("/{item_id}", response_model=ItemReadWithOwner)
@router.patch("/{item_id}", response_model=ItemReadWithOwner)  # actualización parcial
@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
```

Rutas completas y ejemplos:
- `GET /api/v1/items/`
  - Lista ítems. Query: `skip`, `limit`, `owner_id`, `q`, `category_id` (filtra por categoría).
- `POST /api/v1/items/`
  - Crea ítem. Body (ahora admite categorías opcionales):
    ```json
    {"title": "Book", "description": "A book", "owner_id": 1, "category_ids": [1, 2]}
    ```
- `GET /api/v1/items/{item_id}`: obtiene ítem por id (incluye `owner` y `categories`).
- `PUT /api/v1/items/{item_id}`: actualiza parcial. También admite `category_ids` para reemplazo.
- `PATCH /api/v1/items/{item_id}`: actualiza campos puntuales.
- `DELETE /api/v1/items/{item_id}`: borra. `204`.

Respuesta `ItemReadWithOwner` ahora incluye:
```json
{
  "id": 10,
  "title": "Book",
  "description": "A book",
  "owner": {"id": 1, "name": "Alice", "email": "alice@example.com", "role": "user"},
  "categories": [{"id": 1, "name": "Ficción"}, {"id": 2, "name": "Novela"}]
}
```
 
## Endpoints de perfiles (1:1)

`app/api/v1/endpoints/profiles.py`
```python
router = APIRouter(prefix="/profiles", tags=["profiles"])  # bajo /api/v1

@router.get("/me", response_model=ProfileReadWithUser)  # definir antes que /{profile_id}
@router.get("/", response_model=list[ProfileReadWithUser])
@router.post("/", response_model=ProfileReadWithUser)
@router.get("/{profile_id}", response_model=ProfileReadWithUser)
@router.put("/{profile_id}", response_model=ProfileReadWithUser)
@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
```

Rutas completas y ejemplos:
- `GET /api/v1/profiles/` lista perfiles (incluye `user` embebido).
- `POST /api/v1/profiles/` crea perfil (uno por usuario):
  ```json
  {"user_id": 1, "bio": "Hola", "phone": null, "avatar_url": null}
  ```
- `GET /api/v1/profiles/{profile_id}` obtiene por id.
- `PUT /api/v1/profiles/{profile_id}` actualiza parcial.
- `DELETE /api/v1/profiles/{profile_id}` borra (204). Cascada desde `User`.
- `GET /api/v1/profiles/me` devuelve el perfil del usuario autenticado (token o cookie) e incluye `user`.

Nota: Define primero la ruta estática `/profiles/me` y luego la dinámica `/profiles/{profile_id}` para evitar que `me` se intente parsear como entero.

## Endpoints de categorías (N:N con Items)

`app/api/v1/endpoints/categories.py`
```python
router = APIRouter(prefix="/categories", tags=["categories"])  # bajo /api/v1

@router.get("/", response_model=list[CategoryReadWithItems])
@router.post("/", response_model=CategoryRead)
@router.get("/{category_id}", response_model=CategoryReadWithItems)
@router.put("/{category_id}", response_model=CategoryRead)
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
```

Ejemplos:
- `POST /api/v1/categories/`
  ```json
  {"name": "Libros", "description": "Material de lectura"}
  ```
- `GET /api/v1/categories/` devuelve categorías con sus `items` resumidos.
- `GET /api/v1/items?category_id=1` filtra ítems por la categoría dada.

## Dependencias y DB

En ambos routers se usa `Depends(get_db)`:
```python
from app.core.database import get_db
from sqlalchemy.orm import Session

@router.get("/", response_model=list[UserRead])
def list_users(..., db: Session = Depends(get_db)):
    ...
```

`get_db` abre una sesión por request y la cierra al finalizar.

## Endpoints globales

`app/main.py` define:
- `GET /health` → estado del servicio.
- `GET /` → raíz con `{"Hello": "World"}`.
- `GET /scalar` → UI de documentación (no aparece en OpenAPI por `include_in_schema=False`).

## Protección de rutas y roles

Las rutas se protegen mediante JWT y una configuración centralizada.

- Archivo: `app/core/routes_config.py`
- Middleware: `app/core/auth_middleware.py` (registrado en `app/main.py`)

Rutas exactas configuradas:
```python
ROUTES_ACCESS = {
    "/api/v1/login": {"public": True},
    "/api/v1/admin": {"roles": ["admin"]},
    "/api/v1/logout": {"public": True},
}
```

Reglas por prefijo con restricciones por método (para grupos como users/items):
```python
ROUTES_ACCESS_PREFIXES = [
    # Users: lectura para admin/user; escritura solo admin
    {"prefix": "/api/v1/users", "methods": ["GET"], "roles": ["admin", "user"]},
    {"prefix": "/api/v1/users", "methods": ["POST", "PUT", "PATCH", "DELETE"], "roles": ["admin"]},
    # Items: lectura para admin/user/guest; escritura para admin/user
    {"prefix": "/api/v1/items", "methods": ["GET"], "roles": ["admin", "user", "guest"]},
    {"prefix": "/api/v1/items", "methods": ["POST", "PUT", "PATCH", "DELETE"], "roles": ["admin", "user"]},
    # Profiles: lectura y escritura para admin/user
    {"prefix": "/api/v1/profiles", "methods": ["GET", "POST", "PUT", "PATCH", "DELETE"], "roles": ["admin", "user"]},
]
```

Notas de autenticación:
- `POST /api/v1/login` acepta identificador flexible en el campo `email`:
  - Si incluye `@`, se busca por correo.
  - Si no, se busca por nombre de usuario.
 - Al iniciar sesión, se establece un cookie `access_token` (HttpOnly, SameSite=Lax) con el JWT.
   - Esto permite que la UI de documentación en `/scalar` consuma endpoints protegidos sin copiar el token.
 - `POST /api/v1/logout` borra el cookie para cerrar sesión del navegador.

Política por defecto:
- Las rutas no configuradas se consideran públicas y no requieren token.
- Si una ruta está configurada con `roles`, se exige `Authorization: Bearer <token>` y el rol debe estar permitido.

Notas:
- Los usuarios de rol `guest` también requieren autenticación (token) para acceder a sus rutas permitidas.
- Cambia o amplía estas reglas según tus necesidades agregando entradas al archivo de configuración.