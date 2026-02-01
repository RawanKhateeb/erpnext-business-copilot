"""
FastAPI application entry point.
Routes requests to appropriate controllers.
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.middleware.cors import CORSMiddleware
import os
import logging

# Import routers (controllers)
from app.controllers import (
    data_router,
    copilot_router,
    export_router,
    ai_router,
)

logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="ERPNext Business Copilot",
    description="AI-powered assistant for ERPNext business data",
    version="1.0.0"
)

# Add CORS middleware to allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up Jinja2 templates
templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

# Include all routers (controllers)
app.include_router(data_router)
app.include_router(copilot_router)
app.include_router(export_router)
app.include_router(ai_router)


@app.get("/")
def root(request: Request):
    """Serve the Copilot UI homepage."""
    return templates.TemplateResponse("copilot.html", {"request": request})


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


# Mount static files if they exist
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
