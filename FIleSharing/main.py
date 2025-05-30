from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from ops_routes import router as ops_router
from client_routes import router as client_router
from database import create_tables
import os

app = FastAPI()

@app.on_event("startup")
def setup():
    os.makedirs("uploads", exist_ok=True)
    create_tables()

app.mount("/static", StaticFiles(directory="uploads"), name="static")
app.include_router(ops_router, prefix="/ops")
app.include_router(client_router, prefix="/client")