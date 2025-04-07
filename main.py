"""
ZOHOOR - AR Backend API
An AR-enabled e-commerce platform backend using FastAPI.
"""

import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from sqladmin import Admin, ModelView

from routers import auth, carousel
from routers.users import customers, managers, addresses
from routers.good import goods, colors, category, ratings, attr
from routers.inventory import inbound, outbound
from routers.seller import wonders
from routers.order import cart
from routers.store import store
from routers.superusers import visit_stats
from database import engine, Base

from admin.goods import setup_goods_admin
# from middleware.interaction_middleware import InteractionMiddleware
from config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def setup_routers(app: FastAPI) -> None:
    """Configure all application routers."""
    routers = [
        auth.router, customers.router, managers.router,
        addresses.router, carousel.router, goods.router,
        colors.router, category.router, inbound.router,
        outbound.router, wonders.router, ratings.router,
        cart.router, store.router,
        attr.router, visit_stats.router
    ]
    
    for router in routers:
        app.include_router(router)

# def setup_middleware(app: FastAPI) -> None:
#     """Configure application middleware."""
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=settings.BACKEND_CORS_ORIGINS,
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )
#     app.add_middleware(InteractionMiddleware)

def setup_static_files(app: FastAPI) -> None:
    """Configure static file serving."""
    settings.MEDIA_ROOT.mkdir(exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(settings.MEDIA_ROOT)), name="media")

def create_application() -> FastAPI:
    """Initialize and configure the FastAPI application."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        description=f"{settings.PROJECT_NAME} API Documentation",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Initialize database
    Base.metadata.create_all(bind=engine)

    # Setup admin interface
    setup_goods_admin(app, engine)

    # Setup application components
    setup_routers(app)
    # setup_middleware(app)
    setup_static_files(app)
    
    return app

# Initialize application
app = create_application()

@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: HTTPException):
    """Global exception handler for validation errors."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}