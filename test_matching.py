import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, UTC
import uuid

from app.matching_engine import MatchingEngine
from app.models import Order

engine = MatchingEngine()

def reset_engine():
    global engine
    engine = MatchingEngine()

def make_order(**kwargs):
    return Order(
        id=kwargs.get("id", str(uuid.uuid4())),
        timestamp=kwargs.get("timestamp", datetime.now(UTC)),
        symbol=kwargs["symbol"],
        order_type=kwargs["order_type"],
        side=kwargs["side"],
        quantity=kwargs["quantity"],
        price=kwargs.get("price")
    )

def test_limit_order_matching():
    reset_engine()
    sell_order = make_order(symbol="BTC-USDT", order_type="limit", side="sell", quantity=1, price=30000)
    buy_order = make_order(symbol="BTC-USDT", order_type="limit", side="buy", quantity=1, price=30000)

    engine.match_order(sell_order)
    trades = engine.match_order(buy_order)

    assert len(trades) == 1
    assert trades[0].price == 30000
    assert trades[0].quantity == 1

def test_market_order_matching():
    reset_engine()
    engine.match_order(make_order(symbol="BTC-USDT", order_type="limit", side="sell", quantity=2, price=29500))
    market_buy = make_order(symbol="BTC-USDT", order_type="market", side="buy", quantity=1)

    trades = engine.match_order(market_buy)
    assert len(trades) == 1
    assert trades[0].price == 29500
    assert trades[0].quantity == 1

def test_ioc_order():
    reset_engine()
    engine.match_order(make_order(symbol="BTC-USDT", order_type="limit", side="sell", quantity=1, price=31000))
    ioc_buy = make_order(symbol="BTC-USDT", order_type="ioc", side="buy", quantity=2, price=31500)

    trades = engine.match_order(ioc_buy)
    assert len(trades) == 1
    assert trades[0].quantity == 1  # Only 1 available
    # Rest of the order is cancelled automatically

def test_fok_order_fails():
    reset_engine()
    engine.match_order(make_order(symbol="BTC-USDT", order_type="limit", side="sell", quantity=1, price=31000))
    fok_buy = make_order(symbol="BTC-USDT", order_type="fok", side="buy", quantity=2, price=31500)

    trades = engine.match_order(fok_buy)
    assert len(trades) == 0  # Should cancel without any match

def test_fok_order_succeeds():
    reset_engine()
    engine.match_order(make_order(symbol="BTC-USDT", order_type="limit", side="sell", quantity=1, price=31000))
    engine.match_order(make_order(symbol="BTC-USDT", order_type="limit", side="sell", quantity=1, price=31000))
    fok_buy = make_order(symbol="BTC-USDT", order_type="fok", side="buy", quantity=2, price=31500)

    trades = engine.match_order(fok_buy)
    assert len(trades) == 2
    assert sum(t.quantity for t in trades) == 2
