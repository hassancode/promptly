"""API v1 router"""
from fastapi import APIRouter
from .auth import router as auth_router
from .analyses import router as analyses_router
from .prompts import router as prompts_router
from .streaming import router as streaming_router
from .responses import router as responses_router
from .metadata import router as metadata_router
from .insights import router as insights_router

# Create main v1 router
router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include sub-routers
router.include_router(auth_router)
router.include_router(analyses_router)
router.include_router(prompts_router)
router.include_router(streaming_router)
router.include_router(responses_router)
router.include_router(metadata_router)
router.include_router(insights_router)


@router.get("/ping")
async def ping():
    """API v1 ping endpoint"""
    return {"message": "pong", "version": "v1"}
