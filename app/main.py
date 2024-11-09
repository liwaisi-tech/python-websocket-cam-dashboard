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

origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://0.0.0.0:8000",  # Your frontend port
    "http://192.168.1.29:8085",  # Your climate API port
    "http://192.168.1.29",       # Base domain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Added OPTIONS
    allow_headers=["*"],
    expose_headers=["*"]  # Add this line
)

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent
print(f"Base directory: {BASE_DIR}")
print(f"Static directory: {BASE_DIR / 'static'}")

# Configure templates and static files
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
static_dir = BASE_DIR / "static"
if not static_dir.exists():
    raise RuntimeError(f"Static directory does not exist: {static_dir}")

# Add more detailed debug logging
logger.debug(f"Current working directory: {Path.cwd()}")
logger.debug(f"Static files will be served from: {static_dir}")
logger.debug(f"CSS file exists: {(static_dir / 'css' / 'styles.css').exists()}")
logger.debug(f"JS file exists: {(static_dir / 'js' / 'script.js').exists()}")

# List contents of static directory
logger.debug("Static directory contents:")
for item in static_dir.rglob("*"):
    logger.debug(f"  {item.relative_to(static_dir)}")

app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

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
