import asyncio
import logging
import random

logger = logging.getLogger(__name__)

class MockLobEngine:
    def __init__(self):
        self.process = None
        self.best_bid = 50000.0
        self.best_ask = 50005.0
        logger.info("Mock LOB Engine Adapter Initialized (No C++ Required).")

    async def start(self):
        logger.info("Mock LOB Engine Subprocess Started (Simulated).")
        # Creating a dummy object to satisfy 'if not self.process' safety checks
        self.process = asyncio.subprocess.Process
        return self

    async def push_tick(self, price: float, qty: float, side: str):
        """Simulates processing a tick and updating the spread inside Python."""
        if side == "buy" and price > self.best_bid:
            self.best_bid = price
        elif side == "sell" and price < self.best_ask:
            self.best_ask = price
            
        # Keep a tight spread for the simulator
        if self.best_bid >= self.best_ask:
            self.best_ask = self.best_bid + random.uniform(0.5, 5.0)
            
        logger.debug(f"[Mock LOB] Processed {side} tick. Best Bid: {self.best_bid}, Best Ask: {self.best_ask}")

    async def get_best_bid(self) -> float:
        return self.best_bid

    async def get_best_ask(self) -> float:
        return self.best_ask

    async def stop(self):
        logger.info("Mock LOB Engine Subprocess Stopped.")
        self.process = None