from fastapi import APIRouter
from .controllers import  stream

router = APIRouter(prefix="/v1")

# Add all controllers here
router.include_router(stream.router)