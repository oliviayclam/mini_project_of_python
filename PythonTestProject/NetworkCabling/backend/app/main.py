from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import assets, audit, auth, change_requests, dwdm, floor_plans, inventory, orders, reports, search
from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.services.seed import seed_database

# Ensure data directory exists
Path(settings.database_url.replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(orders.router)
app.include_router(change_requests.router)
app.include_router(assets.router)
app.include_router(floor_plans.router)
app.include_router(search.router)
app.include_router(audit.router)
app.include_router(reports.router)
app.include_router(dwdm.router)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name}
