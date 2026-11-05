import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import engine, Base
from app.api.endpoints import router as api_router

# Create tables on startup
Base.metadata.create_all(bind=engine)

# Auto-seed initial admin, patient, clinical rules, and RAG knowledge if empty
try:
    from seed_data import seed_database
    seed_database()
except Exception as e:
    print(f"Notice: database auto-seed skipped or completed: {e}")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Multi-Agent AI Diabetes Support System with ML/DL, RAG, Rule Engine, and Q-Learning.",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "status": "ONLINE",
        "documentation": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

