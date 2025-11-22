from fastapi import APIRouter
from .endpoints import users, items, auth, profiles, categories, products

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(users.router)
api_router.include_router(items.router)
api_router.include_router(auth.router)
api_router.include_router(profiles.router)
api_router.include_router(categories.router)
api_router.include_router(products.router)