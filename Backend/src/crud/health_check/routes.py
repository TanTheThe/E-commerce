from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import APIRouter, Query, status, Depends
from src.cache import redis_manager
from src.dependencies import AccessTokenBearer, admin_role_middleware
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.main import get_session
from fastapi.responses import JSONResponse
from src.errors.user import UserException
import logging

logger = logging.getLogger(__name__)

health_admin_router = APIRouter(prefix="/health")
health_customer_router = APIRouter(prefix="/health")
health_staff_router = APIRouter(prefix="/health")

access_token_bearer = AccessTokenBearer()


@health_admin_router.get("/")
async def health_check() -> Dict[str, str]:
    """Basic health check"""
    return {
        "status": "healthy",
        "service": "e-commerce-api",
        "version": "v1"
    }


@health_admin_router.get("/redis")
async def redis_health() -> Dict[str, Any]:
    """
    Check Redis health and stats
    """
    try:
        health = await redis_manager.health_check()
        return health
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }
        

@health_admin_router.get("/redis/stats")
async def redis_stats() -> Dict[str, Any]:
    """
    Get Redis statistics
    """
    try:
        stats = await redis_manager.get_stats()
        return {
            "status": "ok",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Failed to get Redis stats: {e}")
        return {
            "status": "error",
            "error": str(e)
        }