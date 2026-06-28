import os
import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from src.adapters.mini_kafka_client import MiniKafkaConsumer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Slow-Path Analytics Server")

KAFKA_HOST = os.getenv("MINI_KAFKA_HOST", "127.0.0.1")
KAFKA_PORT = int(os.getenv("MINI_KAFKA_PORT", 8081))


async def _stream_topic(websocket: WebSocket, topic: str):
    await websocket.accept()
    logger.info(f"Dashboard client connected to '{topic}' socket.")
    consumer = MiniKafkaConsumer(host=KAFKA_HOST, port=KAFKA_PORT, topic=topic)
    await consumer.connect()

    try:
        async for message in consumer.consume():
            await websocket.send_json(message)
    except WebSocketDisconnect:
        logger.info(f"Dashboard client disconnected from '{topic}' socket.")
    except Exception as e:
        logger.error(f"Error in '{topic}' WebSocket pipeline: {e}")
    finally:
        await consumer.close()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.websocket("/ws/market")
async def websocket_market_endpoint(websocket: WebSocket):
    await _stream_topic(websocket, "market_data")


@app.websocket("/ws/portfolio")
async def websocket_portfolio_endpoint(websocket: WebSocket):
    await _stream_topic(websocket, "portfolio")
