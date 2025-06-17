from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.matching_engine import MatchingEngine
from app.models import Order, OrderRequest
from app.utils import generate_id, current_timestamp
import asyncio

router = APIRouter()
engine = MatchingEngine()

# Track connected WebSocket clients
orderbook_clients = set()
trade_clients = set()

last_orderbook_state = {"bids": [], "asks": []}

# --- REST endpoint for submitting orders ---
@router.post("/submit_order")
async def submit_order(order_data: OrderRequest):
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
    
    # Trigger push to clients
    asyncio.create_task(broadcast_orderbook())
    asyncio.create_task(broadcast_trades(trades))
    
    return {"order_id": order.id, "trades": [t.__dict__ for t in trades]}

# --- WebSocket endpoint for live order book ---
@router.websocket("/ws/book")
async def ws_book(websocket: WebSocket):
    await websocket.accept()
    orderbook_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(10)  # Keep connection open
    except WebSocketDisconnect:
        orderbook_clients.remove(websocket)

# --- WebSocket endpoint for live trades ---
@router.websocket("/ws/trades")
async def ws_trades(websocket: WebSocket):
    await websocket.accept()
    trade_clients.add(websocket)
    try:
        while True:
            await asyncio.sleep(10)  # Keep connection open
    except WebSocketDisconnect:
        trade_clients.remove(websocket)

# --- Helper: broadcast orderbook changes only when needed ---
async def broadcast_orderbook():
    global last_orderbook_state
    new_state = {
        "bids": engine.order_book.top_levels("buy"),
        "asks": engine.order_book.top_levels("sell")
    }

    if new_state != last_orderbook_state:
        last_orderbook_state = new_state
        dead_clients = set()
        for client in orderbook_clients:
            try:
                await client.send_json(new_state)
            except WebSocketDisconnect:
                dead_clients.add(client)
        orderbook_clients.difference_update(dead_clients)

# --- Helper: broadcast trades when they happen ---
async def broadcast_trades(trades):
    if not trades:
        return
    dead_clients = set()
    for trade in trades:
        for client in trade_clients:
            try:
                await client.send_json(trade.__dict__)
            except WebSocketDisconnect:
                dead_clients.add(client)
    trade_clients.difference_update(dead_clients)
