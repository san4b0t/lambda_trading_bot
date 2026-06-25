import pytest
from pydantic import ValidationError
from src.domain.models import Signal, Side, OrderType, MarketEvent

def test_signal_valid_creation():
    signal = Signal(symbol="BTC/USDT", side=Side.BUY, order_type=OrderType.LIMIT, price=50000.0, quantity=1.5)
    assert signal.symbol == "BTC/USDT"
    assert signal.price == 50000.0

def test_signal_rejects_negative_price():
    with pytest.raises(ValidationError):
        Signal(symbol="BTC/USDT", side=Side.BUY, order_type=OrderType.LIMIT, price=-100.0, quantity=1.0)