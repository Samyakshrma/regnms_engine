from fastapi import APIRouter, WebSocket
from app.matching_engine import MatchingEngine
from app.models import Order , OrderRequest
from app.utils import generate_id, current_timestamp
import asyncio

router = APIRouter()
engine = MatchingEngine()

@router.post("/submit_order")
def submit_order(order_data: OrderRequest):
    order = Order(
        id=generate_id(),
        symbol=order_data.symbol,
        side=order_data.side,
        order_type=order_data.order_type,
        price=order_data.price,
        quantity=order_data.quantity,
        timestamp=current_timestamp()
    )
    trades = engine.match_order(order)
    return {"order_id": order.id, "trades": [t.__dict__ for t in trades]}

@router.websocket("/ws/book")
async def ws_book(websocket: WebSocket):
    await websocket.accept()
    while True:
        await websocket.send_json({
            "bids": engine.order_book.top_levels("buy"),
            "asks": engine.order_book.top_levels("sell")
        })

@router.websocket("/ws/trades")
async def ws_trades(websocket: WebSocket):
    await websocket.accept()
    prev_len = 0
    while True:
        if len(engine.trades) > prev_len:
            new_trades = engine.trades[prev_len:]
            for t in new_trades:
                await websocket.send_json(t.__dict__)
            prev_len = len(engine.trades)