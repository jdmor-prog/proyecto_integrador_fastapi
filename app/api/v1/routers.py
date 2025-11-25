from fastapi import APIRouter
from .endpoints import auth, users, warehouses, products, alerts

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(warehouses.router, prefix="/warehouses", tags=["warehouses"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
