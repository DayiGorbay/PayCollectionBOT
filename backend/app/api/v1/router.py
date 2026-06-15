from fastapi import APIRouter

from app.api.v1 import auth, internal, orders, panels, products, resources, services

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(orders.router)
api_router.include_router(products.router)
api_router.include_router(panels.router)
api_router.include_router(services.router)
api_router.include_router(internal.router)
api_router.include_router(resources.router)
