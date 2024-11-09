from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from core.logger import logger
from api.v1.routes import router as v1_router
from api.health_check.health_check import router as health_check_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Camera Dashboard",
    description="ESP32-CAM Video Stream Dashboard",
    version="1.0.0"
)

# Mount the static directory
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

# Configure templates and static files
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Add root route for the front page
@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

# Include the routers
app.include_router(health_check_router)
app.include_router(v1_router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Application starting up")
    yield
    # Shutdown
    logger.info("Application shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
