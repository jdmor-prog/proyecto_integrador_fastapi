# 02 - Instalación y ejecución

Sigue estos pasos para levantar el proyecto en Windows.

## 1) Crear y activar entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea scripts, ejecuta como administrador:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## 2) Instalar dependencias

```powershell
pip install -r requirements.txt
```

## 3) Configurar variables de entorno (opcional)

El proyecto carga configuración desde `.env` si existe. Ejemplo:
```
APP_NAME="Project Name API"
DATABASE_URL="sqlite:///./project.db"
AUTO_CREATE_TABLES=true
```

## 4) Ejecutar el servidor de desarrollo

```powershell
uvicorn app.main:app --reload
```

- `--reload` recarga en caliente al cambiar archivos.
- Por defecto escucha en `http://127.0.0.1:8000/`.

Endpoints útiles:
- `GET /health` → estado del servicio.
- `GET /scalar` → UI de documentación con Scalar (consume `app.openapi_url`).
 
 ### Autenticación vía cookie y pruebas rápidas
 
 Una vez que el servidor está levantado, puedes autenticarte sin copiar el token gracias a un cookie HttpOnly:
 
 - `POST /api/v1/login` establece un cookie `access_token` (HttpOnly, SameSite=Lax) con el JWT.
 - El middleware autoriza automáticamente peticiones protegidas usando ese cookie cuando no hay header `Authorization`.
 - `POST /api/v1/logout` borra el cookie para cerrar sesión en el navegador.
 
 Pruebas rápidas (PowerShell):
 ```powershell
 # Mantener sesión y usar el cookie sin copiar el token
 $sess = New-Object Microsoft.PowerShell.Commands.WebRequestSession
 $body = @{ email = "admin@example.com"; password = "admin123" } | ConvertTo-Json
 
 # Login: guarda cookie en la sesión
 Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/login' -Method Post -ContentType 'application/json' -Body $body -WebSession $sess
 
 # Acceso protegido sin Authorization:
 Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/profile' -Method Get -WebSession $sess
 
 # Logout: borra cookie
 Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/logout' -Method Post -WebSession $sess
 
 # Verifica que ya no hay acceso (401 esperado)
 Invoke-RestMethod -Uri 'http://127.0.0.1:8000/api/v1/profile' -Method Get -WebSession $sess
 ```
 
 Uso en la UI de Scalar:
 - Abre `http://127.0.0.1:8000/scalar`.
 - Ejecuta `POST /api/v1/login` desde la UI; la cookie se establecerá automáticamente.
 - A partir de entonces, las peticiones protegidas desde la UI se autentican sin copiar el token.
 - Para cerrar la sesión del navegador, usa `POST /api/v1/logout` desde la UI.
 
 Consejos de seguridad (producción):
 - Configura el cookie como `secure=True` (requiere HTTPS).
 - Si `CORS_ALLOW_CREDENTIALS=true`, especifica orígenes permitidos explícitos en `CORS_ALLOW_ORIGINS` (no usar `*`).

## 5) Estructura de base de datos

- Por defecto usa `sqlite:///./project.db`.
- En `startup` se crea el esquema si `AUTO_CREATE_TABLES=true`.

## 6) Seeds: usuarios de prueba

Para crear usuarios de prueba (admin, users, guests) ejecuta:

```powershell
python scripts/seed_users.py
```

- Opción de reseteo (elimina y vuelve a crear las tablas antes de sembrar):

```powershell
python scripts/seed_users.py --reset
```

- Alternativa (evita errores de import en algunos entornos):

```powershell
python -m scripts.seed_users --reset
```

- Vaciar la base sin sembrar (dejar tablas vacías):

```powershell
python -m scripts.seed_users --empty
```

Usuarios creados:
- Admin: `admin@example.com / admin123`
- Users: `user1@example.com`, `user2@example.com`, `user3@example.com` (password `user123`)
- Guests: `guest1@example.com`, `guest2@example.com` (password `guest123`)

Notas:
- `--reset` ejecuta `drop_all` y luego `create_all`, útil si cambiaste el modelo `User`.
- `--empty` también `drop_all` + `create_all`, pero sin sembrar.
- Asegúrate de tener el entorno virtual activado y dependencias instaladas.

## 7) Problemas comunes

- "DLL load failed" o similares → reinstala dependencias o usa Python 3.11+.
- Permisos de PowerShell → ver sección de ExecutionPolicy arriba.
- "database is locked" en SQLite → cierra procesos concurrentes, evita dos servidores activos.