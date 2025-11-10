# Centralized route access control configuration
# Define which routes are public or which roles are allowed

# Exact path configuration
ROUTES_ACCESS = {
    "/api/v1/login": {"public": True},
    "/api/v1/logout": {"public": True},
    "/api/v1/admin": {"roles": ["admin"]},
    "/api/v1/profile": {"roles": ["admin", "user"]},
}

# Prefix-based configuration for resource groups (supports method-specific roles)
ROUTES_ACCESS_PREFIXES = [
    # Users: read for admin/user; write only admin
    {"prefix": "/api/v1/users", "methods": ["GET"], "roles": ["admin", "user"]},
    {"prefix": "/api/v1/users", "methods": ["POST", "PUT", "PATCH", "DELETE"], "roles": ["admin"]},
    # Items: read for admin/user/guest; write for admin/user
    {"prefix": "/api/v1/items", "methods": ["GET"], "roles": ["admin", "user", "guest"]},
    {"prefix": "/api/v1/items", "methods": ["POST", "PUT", "PATCH", "DELETE"], "roles": ["admin", "user"]},
    # Categories: read for admin/user/guest; write for admin/user
    {"prefix": "/api/v1/categories", "methods": ["GET"], "roles": ["admin", "user", "guest"]},
    {"prefix": "/api/v1/categories", "methods": ["POST", "PUT", "PATCH", "DELETE"], "roles": ["admin", "user"]},
    # Profiles: lectura y escritura para admin y user
    {"prefix": "/api/v1/profiles", "methods": ["GET"], "roles": ["admin", "user"]},
    {"prefix": "/api/v1/profiles", "methods": ["POST", "PUT", "PATCH", "DELETE"], "roles": ["admin", "user"]},
]