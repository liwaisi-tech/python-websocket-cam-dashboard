from fastapi import APIRouter
from fastapi.responses import JSONResponse
import httpx
from core.logger import logger

router = APIRouter(prefix="/climate", tags=["Climate"])

CLIMATE_API_URL = "http://192.168.1.29:8085/v1/liwaisi-iot/api/climate/latest"

@router.get("/latest")
async def get_latest_climate():
    """
    Proxy endpoint to fetch latest climate data
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(CLIMATE_API_URL)
            if response.status_code == 200:
                return JSONResponse(
                    status_code=200,
                    content=response.json()
                )
            else:
                logger.error(f"Climate API error: {response.status_code}")
                return JSONResponse(
                    status_code=502,
                    content={"error": "Failed to fetch climate data"}
                )
    except Exception as e:
        logger.error(f"Error fetching climate data: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error"}
        ) 