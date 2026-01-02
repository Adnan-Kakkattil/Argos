"""
API v1 Router
"""
from fastapi import APIRouter

api_router = APIRouter()

# Import and include routers
from backend.api.v1.endpoints import auth, platform_admin, tenant, agent

api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(platform_admin.router, prefix="/platform-admin", tags=["platform-admin"])
api_router.include_router(tenant.router, prefix="/tenant", tags=["tenant"])
api_router.include_router(agent.router, prefix="/agent", tags=["agent"])

