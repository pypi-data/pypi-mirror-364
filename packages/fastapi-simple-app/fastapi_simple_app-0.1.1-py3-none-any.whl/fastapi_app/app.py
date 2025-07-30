
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

app = FastAPI()

# Konfiguracja CORS (dla frontendów lokalnych lub zewnętrznych)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Możesz ograniczyć do np. ["http://localhost:3000"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ścieżka do folderu frontend w paczce
current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.join(current_dir, "static")

# Serwowanie plików statycznych (np. JS, CSS)
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

# Endpoint API
@app.get("/api/data")
def get_data():
    return {"message": "Hello from FastAPI backend!"}

# Serwowanie index.html jako strona główna
@app.get("/")
def serve_frontend():
    return FileResponse(os.path.join(frontend_dir, "index.html"))
