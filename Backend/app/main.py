import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine, Base, SessionLocal
from app.routers import auth, rates, scrap, pickups, dashboard
from app.routers.rates import seed_default_rates_if_empty

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: ensure upload dir and database tables exist
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_default_rates_if_empty(db)
        auth.seed_default_users(db)
    finally:
        db.close()
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    description="""
    ## ScrapSetu REST API ♻️
    Backend service connecting Scrap Collectors and Recyclers seamlessly.
    
    ### Key Features:
    * **Authentication & Profile**: Mobile & password login/registration with JWT tokens.
    * **Live Scrap Rates**: Pre-seeded rates for Plastic, Paper, Iron, Copper, Aluminium, Steel, E-Waste.
    * **Scrap Lots Workflow**: Collector submissions -> Recycler incoming view -> Accept/Reject -> Pickup -> Handover & Completion.
    * **Pickup & Logistics Tracking**: Scheduled pickups, tracking steps, driver assignment.
    * **Analytics & Dashboard**: Metrics for recycled volumes, values, and material breakdowns.
    """,
    lifespan=lifespan
)

# CORS Middleware (permits frontend calls from localhost, file://, etc.)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploaded files
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(rates.router, prefix=settings.API_V1_STR)
app.include_router(scrap.router, prefix=settings.API_V1_STR)
app.include_router(pickups.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc"
    }
