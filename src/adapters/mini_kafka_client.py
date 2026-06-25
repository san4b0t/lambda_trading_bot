import json
import asyncio
import logging

logger = logging.getLogger(__name__)

class MiniKafkaProducer:
    def __init__(self, host: str = "127.0.0.1", port: int = 9092):
        self.host = host
        self.port = port
        self.writer = None

    async def connect(self):
        _, self.writer = await asyncio.open_connection(self.host, self.port)
        logger.info(f"Connected to Mini-Kafka Producer at {self.host}:{self.port}")

    async def publish(self, topic: str, message: dict):
        if not self.writer:
            raise RuntimeError("Producer not connected to Mini-Kafka.")
        payload = json.dumps({"topic": topic, "data": message}) + "\n"
        self.writer.write(payload.encode())
        await self.writer.drain()

class MiniKafkaConsumer:
    def __init__(self, host: str = "127.0.0.1", port: int = 9092, topic: str = "market_data"):
        self.host = host
        self.port = port
        self.topic = topic
        self.reader = None
        self.writer = None

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection(self.host, self.port)
        subscribe_msg = json.dumps({"action": "subscribe", "topic": self.topic}) + "\n"
        self.writer.write(subscribe_msg.encode())
        await self.writer.drain()
        logger.info(f"Subscribed to Mini-Kafka topic: {self.topic}")

    async def consume(self):
        while True:
            try:
                data = await self.reader.readline()
                if not data:
                    break
                yield json.loads(data.decode())
            except Exception as e:
                logger.error(f"Error consuming from Mini-Kafka: {e}")
                break