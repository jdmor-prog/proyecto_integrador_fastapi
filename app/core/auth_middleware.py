from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from app.core.routes_config import ROUTES_ACCESS, ROUTES_ACCESS_PREFIXES
from app.core.security import decode_token


class RoleAuthMiddleware(BaseHTTPMiddleware):
    """Authorization middleware based on JWT and centralized route config.
    Validates bearer token and roles for protected endpoints.
    """

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path
        method = request.method.upper()

        access_cfg = ROUTES_ACCESS.get(path)
        prefix_cfg = None
        if not access_cfg:
            # Try prefix-based rules with optional method constraints
            for cfg in ROUTES_ACCESS_PREFIXES:
                prefix = cfg.get("prefix")
                methods = cfg.get("methods")
                if path.startswith(prefix) and (methods is None or method in methods):
                    prefix_cfg = cfg
                    break

        effective_cfg = access_cfg or prefix_cfg
        # If route not configured, let it pass (public by default)
        if not effective_cfg:
            return await call_next(request)
        # If explicitly public, let it pass
        if effective_cfg.get("public"):
            return await call_next(request)

        # For protected routes, require JWT via Authorization header or HttpOnly cookie
        auth_header = request.headers.get("Authorization", "")
        token = None
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1]
        else:
            # Fallback to cookie set by /login for browser-based clients (Scalar docs, etc.)
            token = request.cookies.get("access_token")
            if not token:
                return JSONResponse({"detail": "Autorización requerida"}, status_code=401)
        try:
            payload = decode_token(token)
        except Exception as e:
            # decode_token already maps specific errors to 401
            if isinstance(e, JSONResponse):
                return e
            return JSONResponse({"detail": "Token inválido"}, status_code=401)

        # Attach claims to request state for downstream usage
        request.state.user_id = payload.get("sub")
        request.state.email = payload.get("email")
        request.state.role = payload.get("role")

        # If roles are specified, enforce them
        if effective_cfg and "roles" in effective_cfg:
            allowed = effective_cfg["roles"]
            if request.state.role not in allowed:
                return JSONResponse({"detail": "Permisos insuficientes"}, status_code=403)

        return await call_next(request)