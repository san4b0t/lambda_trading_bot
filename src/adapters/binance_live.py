import ccxt.async_support as ccxt
import os
import logging

logger = logging.getLogger(__name__)

class BinanceLiveAdapter:
    def __init__(self):
        self.exchange = ccxt.binance({
            'apiKey': os.getenv('BINANCE_TESTNET_API_KEY'),
            'secret': os.getenv('BINANCE_TESTNET_API_SECRET'),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })

        self.exchange.set_sandbox_mode(True)
        logger.info("Binance Adapter Initialized in SANDBOX (Testnet) Mode.")

    async def fetch_balance(self) -> float:
        try:
            balance = await self.exchange.fetch_balance()
            return float(balance['total'].get('USDT', 0.0))
        except Exception as e:
            logger.error(f"Failed to fetch balance from Binance: {e}")
            return 0.0

    async def create_order(self, symbol: str, type: str, side: str, amount: float, price: float) -> dict:
        try:
            logger.info(f"Routing live order to Binance -> {side.upper()} {amount} {symbol} @ {price}")
            order = await self.exchange.create_order(symbol, type, side, amount, price)
            return order
        except Exception as e:
            logger.error(f"Order placement failed on Binance gateway: {e}")
            raise

    async def close(self):
        await self.exchange.close()