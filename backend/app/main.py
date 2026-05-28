from fastapi import FastAPI
from .api.health import router as health_router
from .api.uploads import router as upload_router


app = FastAPI(
    title="MediScan RAG Backend",
    description="FastAPI backend for the MediScan RAG medical intelligence assistant.",
    version="0.1.0",
)

app.include_router(health_router, prefix="/api")
app.include_router(upload_router, prefix="/api")

@app.get("/")
def read_root():
    return {"status": "ok", "message": "MediScan RAG backend is running."}
