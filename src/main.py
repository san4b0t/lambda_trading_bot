import asyncio
import os
import logging
import redis.asyncio as redis
from dotenv import load_dotenv
from src.adapters.binance_live import BinanceLiveAdapter
from src.adapters.lob_wrapper import LocalLobEngine
from src.adapters.lob_mock import MockLobEngine
from src.adapters.mini_kafka_client import MiniKafkaProducer
from src.core.risk_manager import RiskManager
from src.domain.models import Signal, Side, OrderType

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def fast_path_ingestion(lob: LocalLobEngine, producer: MiniKafkaProducer, cache: redis.Redis):
    """Simulates real-time market data ticks flowing to C++, Redis cache, and Mini-Kafka."""
    mock_base_price = 45000.0
    tick_counter = 0
    
    while True:
        tick_counter += 1
        current_price = mock_base_price + (tick_counter % 10 * 0.5)
        side = "buy" if tick_counter % 2 == 0 else "sell"
        
        await lob.push_tick(current_price, 1.5, side)
        await cache.set("BTC_BEST_BID", str(current_price))
        await producer.publish("market_data", {"symbol": "BTC/USDT", "price": current_price, "side": side})
        
        await asyncio.sleep(0.05)

async def execution_strategy_loop(binance: BinanceLiveAdapter, risk: RiskManager, producer: MiniKafkaProducer, cache: redis.Redis):
    symbol = "BTC/USDT"
    
    while True:

        current_equity = await binance.fetch_balance()
        risk.update_equity(current_equity)

        await producer.publish("portfolio", {"balance": current_equity})
        
        if not risk.allow_trade():
            logger.critical("Strategy Execution Loop Forced Stopped by Risk Management.")
            break
            
        best_bid_bytes = await cache.get("BTC_BEST_BID")
        if best_bid_bytes:
            best_bid = float(best_bid_bytes)
            
            if best_bid > 0:
                signal = Signal(symbol=symbol, side=Side.BUY, order_type=OrderType.LIMIT, price=best_bid - 0.5, quantity=0.002)
                
                try:
                   
                    receipt = await binance.create_order(
                        signal.symbol, signal.order_type.value, signal.side.value, signal.quantity, signal.price
                    )
                    
                    await producer.publish("trade_executions", receipt)
                except Exception as e:
                    logger.error(f"Strategy failed to execute valid signal: {e}")

        await asyncio.sleep(1.0)

async def main():
    load_dotenv()
    
    binance = BinanceLiveAdapter()
    lob = LocalLobEngine()
    kafka_producer = MiniKafkaProducer(
        host=os.getenv("MINI_KAFKA_HOST", "127.0.0.1"),
        port=int(os.getenv("MINI_KAFKA_PORT", 8081))
    )
    cache = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"), 
        port=int(os.getenv("REDIS_PORT", 6379)), 
        db=0
    )
    risk = RiskManager(max_drawdown_pct=float(os.getenv("MAX_DRAWDOWN_PCT", 0.08)))

    # Start low-level components
    await lob.start()
    await kafka_producer.connect()

    logger.info("Initialization complete. Firing up concurrent execution tracks.")
    try:
        await asyncio.gather(
            fast_path_ingestion(lob, kafka_producer, cache),
            execution_strategy_loop(binance, risk, kafka_producer, cache)
        )
    except asyncio.CancelledError:
        logger.warning("System threads caught cancel signal. Tearing down safely.")
    finally:
        await binance.close()
        await kafka_producer.close()
        await cache.aclose()
        if lob.process and lob.process.returncode is None:
            lob.process.terminate()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot manually terminated via SIGINT.")