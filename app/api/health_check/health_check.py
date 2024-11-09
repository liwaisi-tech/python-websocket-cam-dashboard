from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/health-check", tags=["Health Check"])

@router.get("")
async def health_check():
    """
    Health check endpoint to verify API is running
    """
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "service": "camera-dashboard"
        }
    ) 