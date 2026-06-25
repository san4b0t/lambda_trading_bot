from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.adapters.mini_kafka_client import MiniKafkaConsumer
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Slow-Path Analytics Server")

@app.websocket("/ws/market")
async def websocket_market_endpoint(websocket: WebSocket):
    await websocket.accept()
    logger.info("Dashboard client connected to Live Market socket.")
    
    consumer = MiniKafkaConsumer(topic="market_data")
    await consumer.connect()
    
    try:
        async for message in consumer.consume():
            await websocket.send_json(message)
    except WebSocketDisconnect:
        logger.info("Dashboard client disconnected from Market socket.")
    except Exception as e:
        logger.error(f"Error in API WebSocket pipeline: {e}")