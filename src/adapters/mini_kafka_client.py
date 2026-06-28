import json
import asyncio
import aiohttp
import logging

logger = logging.getLogger(__name__)

# The mini-kafka Go broker is a pure HTTP append-only log. Its real API is:
#   POST /topics/{topic}/messages      -> append raw bytes, returns {"offset": N} (201)
#   GET  /topics/{topic}/messages?offset=X -> raw bytes (200), or 404 at end-of-log / unknown topic
# Topics are auto-created on first publish, so no explicit topic creation is required.


class MiniKafkaProducer:
    def __init__(self, host: str = "127.0.0.1", port: int = 8081):
        self.base_url = f"http://{host}:{port}"
        self.session: aiohttp.ClientSession | None = None
        logger.info(f"HTTP Producer initialized for {self.base_url}")

    async def connect(self):
        # Initialize the persistent HTTP session
        self.session = aiohttp.ClientSession()
        logger.info("HTTP Client Session opened.")

    async def publish(self, topic: str, message: dict):
        if not self.session:
            raise RuntimeError("Producer session not initialized.")

        # Preserve the {topic, data} envelope the dashboard consumes.
        url = f"{self.base_url}/topics/{topic}/messages"
        try:
            body = json.dumps({"topic": topic, "data": message}).encode()
        except (TypeError, ValueError) as e:
            logger.error(f"Refusing to publish non-serializable payload to '{topic}': {e}")
            return

        try:
            async with self.session.post(
                url, data=body, headers={"Content-Type": "application/octet-stream"}
            ) as response:
                # Broker returns 201 Created on a successful append.
                if response.status not in (200, 201):
                    logger.warning(f"Broker returned status {response.status} publishing to '{topic}'")
        except Exception as e:
            logger.error(f"Failed to publish to broker: {e}")

    async def close(self):
        if self.session:
            await self.session.close()
            logger.info("HTTP Client Session safely closed.")


class MiniKafkaConsumer:
    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 8081,
        topic: str = "market_data",
        poll_interval: float = 0.1,
        from_latest: bool = True,
    ):
        self.base_url = f"http://{host}:{port}"
        self.topic = topic
        self.poll_interval = poll_interval
        self.from_latest = from_latest
        self.offset = 0
        self.session: aiohttp.ClientSession | None = None

    async def connect(self):
        self.session = aiohttp.ClientSession()
        if self.from_latest:
            # Skip historical backlog so a freshly-opened dashboard sees live data only.
            self.offset = await self._find_tail()
        logger.info(f"Consumer for topic '{self.topic}' starting at offset {self.offset}.")

    async def _find_tail(self) -> int:
        """Fast-forward through any existing messages to find the next free offset."""
        url = f"{self.base_url}/topics/{self.topic}/messages"
        offset = 0
        while True:
            try:
                async with self.session.get(url, params={"offset": offset}) as response:
                    if response.status == 200:
                        await response.read()
                        offset += 1
                        continue
                    # 404 -> topic not created yet or we've reached the end of the log.
                    return offset
            except Exception as e:
                logger.error(f"Error scanning to tail of '{self.topic}': {e}")
                return offset

    async def consume(self):
        if not self.session:
            raise RuntimeError("Consumer session not initialized.")

        url = f"{self.base_url}/topics/{self.topic}/messages"
        while True:
            try:
                async with self.session.get(url, params={"offset": self.offset}) as response:
                    if response.status == 200:
                        raw = await response.read()
                        self.offset += 1
                        try:
                            yield json.loads(raw.decode())
                        except json.JSONDecodeError:
                            yield {"raw": raw.decode(errors="replace")}
                    elif response.status == 404:
                        # End of partition (or topic not created yet) -> wait and retry.
                        await asyncio.sleep(self.poll_interval)
                    else:
                        logger.warning(f"Unexpected status {response.status} consuming '{self.topic}'")
                        await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error consuming from Mini-Kafka: {e}")
                await asyncio.sleep(self.poll_interval)

    async def close(self):
        if self.session:
            await self.session.close()
