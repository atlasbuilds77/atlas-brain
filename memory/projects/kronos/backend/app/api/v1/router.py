"""API v1 Router - Main API routing"""

from fastapi import APIRouter
from app.api.v1.endpoints import auth, leads, clients, messages, files, analytics

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(leads.router, prefix="/leads", tags=["Leads"])
api_router.include_router(clients.router, prefix="/clients", tags=["Clients"])
api_router.include_router(messages.router, prefix="/messages", tags=["Messages"])
api_router.include_router(files.router, prefix="/files", tags=["Files"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
