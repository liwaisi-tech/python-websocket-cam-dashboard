from fastapi import APIRouter
from .controllers import stream, climate

router = APIRouter(prefix="/v1")

# Add all controllers here
router.include_router(stream.router)
router.include_router(climate.router)