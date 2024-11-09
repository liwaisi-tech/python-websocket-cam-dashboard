from fastapi import APIRouter, WebSocket
from fastapi.responses import JSONResponse
from core.logger import logger
import asyncio
import websockets

router = APIRouter(prefix="/stream", tags=["Stream"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
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
    try:
        await websocket.accept()
        logger.info("Client connected")
        
        # Use websockets library to connect to external stream
        source_ws = await websockets.connect("ws://192.168.1.48/ws")
        while True:
            try:
                # Receive frame from source websocket
                frame_base64 = await source_ws.recv()
                try:
                    # Forward frame to client
                    await websocket.send_text(frame_base64)
                    await asyncio.sleep(0.033)  # ~30 FPS
                except Exception as e:
                    logger.error(f"Error sending frame: {str(e)}")
                    break
                    
            except Exception as e:
                logger.error(f"Error receiving frame from source: {str(e)}")
                break
                
    except Exception as e:
        logger.error(f"Stream error: {str(e)}")
    finally:
        manager.disconnect(websocket)
        try:
            await source_ws.close()
        except Exception as e:
            print(f"Error closing WebSocket: {e}")
            pass

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
