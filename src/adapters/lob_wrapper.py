import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class LocalLobEngine:
    def __init__(self, binary_path: str = "./third_party/lob-engine/build_release/lob_simulator"):
        self.binary_path = binary_path
        self.process = None

    async_support = True

    async def start(self):
        try:
            self.process = await asyncio.create_subprocess_exec(
                self.binary_path,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            logger.info("Successfully spun up local C++ LOB Engine subprocess.")
        except Exception as e:
            logger.critical(f"Failed to start C++ LOB Engine binary at {self.binary_path}: {e}")
            raise

    async def push_tick(self, price: float, qty: float, side: str):
        if not self.process or self.process.returncode is not None:
            raise RuntimeError("C++ LOB Engine subprocess is dead or uninitialized.")
        
        payload = json.dumps({"action": "add", "price": price, "qty": qty, "side": side}) + "\n"
        self.process.stdin.write(payload.encode())
        await self.process.stdin.drain()