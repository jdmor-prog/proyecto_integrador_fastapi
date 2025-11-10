# 11 - Solución de problemas (FAQ)

## 1) Scalar no muestra todos los endpoints
- Verifica que solo existe una instancia de `app` en `main.py`.
- Asegúrate de haber llamado `app.include_router(api_router)`.
- Comprueba `api/v1/routers.py`: deben incluirse `users.router` e `items.router`.
- Evita `include_in_schema=False` salvo en rutas que no quieras documentar.

## 2) Error de CORS al abrir `/scalar`
- Usa `scalar_proxy_url="https://proxy.scalar.com"` como en `main.py`.
- Configura CORS con `fastapi.middleware.cors` si expones la API a frontends externos.

## 3) "database is locked" en SQLite
- No corras dos instancias de servidor usando la misma DB.
- Evita largas transacciones; confirma `db.commit()` oportunamente.

## 4) Problemas al instalar dependencias
- Asegúrate de activar `.venv` antes de `pip install -r requirements.txt`.
- Usa Python 3.11+ compatible con las versiones de las dependencias.

## 5) Migraciones de esquema
- Para producción, usa `Alembic` en lugar de `create_all` en `startup`.

## 6) Rutas 404
- Confirma el prefijo correcto: `GET /api/v1/users/` (no falta `/api/v1`).
- Revisa `routers.py` y que el archivo esté importado en `main.py`.

## 7) Validación Pydantic
- Si la validación falla, revisa tipos en schemas (`EmailStr`, `int`, `str`).
- Asegúrate de enviar payload con claves correctas.

## 7.1) Error de validación del email en login

- Síntoma:
  - Respuesta similar a:
    ```json
    {
      "detail": [
        {
          "type": "value_error",
          "loc": ["body", "email"],
          "msg": "value is not a valid email address: An email address must have an @-sign.",
          "input": "Admin"
        }
      ]
    }
    ```
- Causa:
  - El campo `email` se valida como identificador. Si tiene `@`, se considera correo y debe ser válido.
- Solución:
  - Envía correo válido, por ejemplo `admin@example.com`, o usa nombre de usuario en el mismo campo.
  - Ejemplos:
    ```bash
    # Por email
    curl -X POST "http://localhost:8000/api/v1/login" \
      -H "Content-Type: application/json" \
      -d '{"email":"admin@example.com","password":"admin123"}'

    # Por nombre
    curl -X POST "http://localhost:8000/api/v1/login" \
      -H "Content-Type: application/json" \
      -d '{"email":"Admin","password":"admin123"}'
    ```

## 8) Seeder no funciona

Síntomas y soluciones:
- `ModuleNotFoundError: No module named 'app'`
  - Ejecuta el comando desde la raíz del proyecto (`project_name/`).
  - Activa el entorno virtual: `\.venv\Scripts\Activate.ps1`.
  - Usa: `python -m scripts.seed_users --reset`.
  - Alternativa: `python scripts/seed_users.py --reset` (el script añade la raíz al `sys.path`).
- `sqlite3.OperationalError: table users has no column named hashed_password`
  - La DB tiene un esquema antiguo. Usa `--reset` para recrear tablas:
    - `python scripts/seed_users.py --reset`
  - Esto ejecuta `drop_all` seguido de `create_all`; perderás datos previos.
- Dependencias faltantes (`bcrypt`, `PyJWT`)
  - Instala: `pip install -r requirements.txt`.
- Versión de Python incompatible
  - Usa `python --version` y confirma 3.11+. Si no, instala Python reciente.