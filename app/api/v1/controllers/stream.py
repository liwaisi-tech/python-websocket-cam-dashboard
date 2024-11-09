from fastapi import APIRouter, WebSocket
from fastapi.responses import JSONResponse
from core.logger import logger
import asyncio
import websockets

router = APIRouter(prefix="/stream", tags=["Stream"])

# Add these constants at the top of the file
MAX_RECONNECTION_ATTEMPTS = 3
RECONNECTION_DELAY = 5  # seconds
ESP32_WEBSOCKET_URL = "ws://192.168.1.48/ws"

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        try:
            self.active_connections.remove(websocket)
        except ValueError:
            # Connection was already removed or never existed
            pass
        logger.info(f"Client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {str(e)}")

manager = ConnectionManager()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    source_ws = None
    reconnection_attempts = 0
    
    async def connect_to_camera():
        try:
            return await websockets.connect(ESP32_WEBSOCKET_URL)
        except Exception as e:
            logger.error(f"Failed to connect to camera: {str(e)}")
            return None

    try:
        await websocket.accept()
        logger.info("Client connected")
        
        while True:
            if source_ws is None:
                if reconnection_attempts >= MAX_RECONNECTION_ATTEMPTS:
                    logger.error("Max reconnection attempts reached")
                    await websocket.send_text("Camera connection failed after maximum retries")
                    break
                
                source_ws = await connect_to_camera()
                if source_ws is None:
                    reconnection_attempts += 1
                    logger.info(f"Retrying connection in {RECONNECTION_DELAY} seconds... (Attempt {reconnection_attempts}/{MAX_RECONNECTION_ATTEMPTS})")
                    await asyncio.sleep(RECONNECTION_DELAY)
                    continue
                else:
                    reconnection_attempts = 0  # Reset counter on successful connection
                    
            try:
                frame_base64 = await source_ws.recv()
                try:
                    await websocket.send_text(frame_base64)
                    await asyncio.sleep(0.033)  # ~30 FPS
                except Exception as e:
                    logger.error(f"Error sending frame to client: {str(e)}")
                    break
                    
            except websockets.exceptions.ConnectionClosed:
                logger.warning("Camera connection closed. Attempting to reconnect...")
                await source_ws.close()
                source_ws = None
                
            except Exception as e:
                logger.error(f"Error receiving frame from source: {str(e)}")
                source_ws = None  # Force reconnection attempt
                
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
    finally:
        manager.disconnect(websocket)
        if source_ws:
            try:
                await source_ws.close()
            except Exception as e:
                logger.error(f"Error closing camera WebSocket: {e}")

@router.get("/status")
async def stream_status():
    """
    Get the current status of active stream connections
    """
    return JSONResponse(
        status_code=200,
        content={
            "active_connections": len(manager.active_connections),
            "status": "running"
        }
    )
