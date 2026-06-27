import pytest
from fastapi.testclient import TestClient
from src.api.ws_server import app
from unittest.mock import AsyncMock

client = TestClient(app)

def test_websocket_market_stream(mocker):
    # We mock the Kafka consumer so it yields a fake message instead of connecting to a real broker
    mock_consumer = mocker.patch("src.api.ws_server.MiniKafkaConsumer")
    instance = mock_consumer.return_value
    instance.connect = AsyncMock()
    
    # Create an async generator that yields one fake market tick
    async def fake_consume():
        yield {"topic": "market_data", "data": {"symbol": "BTC/USDT", "price": 50000.0, "side": "buy"}}
    
    instance.consume = fake_consume

    # Connect to the FastAPI websocket using the TestClient
    with client.websocket_connect("/ws/market") as websocket:
        data = websocket.receive_json()
        assert data["topic"] == "market_data"
        assert data["data"]["price"] == 50000.0