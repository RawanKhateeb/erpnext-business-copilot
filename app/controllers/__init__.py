"""Controllers package - Route handlers."""
from fastapi import APIRouter

from app.controllers.data import router as data_router
from app.controllers.copilot import router as copilot_router
from app.controllers.export import router as export_router
from app.controllers.ai import router as ai_router

__all__ = ["data_router", "copilot_router", "export_router", "ai_router"]
