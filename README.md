


# 🚀 Crypto Matching Engine 

A high-performance cryptocurrency order matching engine built with **FastAPI** and **WebSocket**. Designed in accordance with **REG NMS-inspired rules**, this engine ensures:

- ✅ Price-Time Priority  
- ✅ Internal Order Protection  
- ✅ Real-time Order Book & Trade Stream  

---

## 🧠 Features

- ⚡ **Supports Order Types**: `Market`, `Limit`, `IOC`, and `FOK`
- 🏛 **Matching Algorithm**: Enforces strict FIFO (First In, First Out) within price levels
- 🔄 **Real-Time Data** via WebSockets:
  - Order Book (top levels + BBO)
  - Trade Executions
- 💥 Partial fills, trade-through protection, and clean order life-cycle

---

## 🧱 System Architecture



```
    +-----------------+         +--------------------+
    |   REST Client   | ----->  |  /submit_order API |
    +-----------------+         +--------------------+
                                      |
                                      v
                             +-------------------+
                             | Matching Engine   |
                             | (In-Memory Book)  |
                             +-------------------+
                             /         \
                            /           \
        +---------------------+     +---------------------+
        | ws/book WebSocket   |     | ws/trades WebSocket |
        | Streams Order Book  |     | Streams Trade Events|
        +---------------------+     +---------------------+
```



---

## 📦 API Reference

### 📥 `POST /submit_order`

Submit a new order to the matching engine.

**Request Body:**
```json
{
  "symbol": "BTC-USDT",
  "order_type": "limit",
  "side": "buy",
  "price": 25000.5,
  "quantity": 1.2
}
````

**Response:**

```json
{
  "order_id": "abcd1234",
  "trades": [
    {
      "trade_id": "xyz987",
      "price": 25000.5,
      "quantity": 1.2,
      "maker_order_id": "...",
      "taker_order_id": "...",
      "aggressor_side": "buy",
      "timestamp": "..."
    }
  ]
}
```

---

### 📡 `WebSocket /ws/book`

Streams the **top levels of the order book** continuously (BBO - Best Bid & Offer).

**Sample Response:**

```json
{
  "bids": [[25000.5, 1.0], [24950.0, 0.5]],
  "asks": [[25010.0, 0.8], [25020.0, 1.2]]
}

```

---

### ⚡ `WebSocket /ws/trades`

Streams **live trade executions** in real-time.

**Sample Response:**

```json
{
  "trade_id": "t12345",
  "symbol": "BTC-USDT",
  "price": "25000.5",
  "quantity": "1.0",
  "maker_order_id": "...",
  "taker_order_id": "...",
  "aggressor_side": "buy",
  "timestamp": "2025-06-16T14:25:06.123456Z"
}
```

---

## 🧩 Matching Engine Logic

* Orders are stored in a price-level sorted book (buy: descending, sell: ascending).
* Marketable orders are matched against the best prices first.
* FIFO matching within each price level.
* IOC orders are partially matched and rest discarded.
* FOK orders cancel if not fully matched instantly.

---

## 🧪 Example Order Types

| Type   | Description                                      |
| ------ | ------------------------------------------------ |
| Market | Executes at the best available price             |
| Limit  | Executes at price or better; rests if not filled |
| IOC    | Fills immediately, cancels unfilled remainder    |
| FOK    | Fills entire amount immediately or cancels       |

---

## 🛠 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Samyakshrma/regnms_engine.git
cd regnms_engine
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the FastAPI server

```bash
uvicorn app.main:app --reload
```
---
## 🔍 Testing API

* 📬 Use [Postman](https://www.postman.com/) or Swagger UI (`http://localhost:8000/docs`) to submit orders via the `POST /submit_order` endpoint.



Make sure your FastAPI app is up and running:

```bash
uvicorn app.main:app --reload
```


#### ✅ 1. Submit a Buy Limit Order

**Request:**

* **Method**: `POST`
* **URL**: `http://localhost:8000/submit_order`
* **Headers**:

  * `Content-Type: application/json`

**Body:**

```json
{
  "symbol": "BTC-USD",
  "side": "buy",
  "order_type": "limit",
  "price": 100,
  "quantity": 1
}
```

**Expected Response:**

```json
{
  "order_id": "some-uuid",
  "trades": []
}
```



#### ✅ 2. Submit a Matching Sell Order

**Body:**

```json
{
  "symbol": "BTC-USD",
  "side": "sell",
  "order_type": "limit",
  "price": 100,
  "quantity": 1
}
```

**Response:**

```json
{
  "order_id": "some-uuid",
  "trades": [
    {
      "trade_id": "unique_id",
      "symbol": "BTC-USD",
      "price": 100,
      "quantity": 1.0,
      "timestamp": "2025-06-16T21:37:45.913412",
      "maker_order_id": "resting_order_id",
      "taker_order_id": "incoming_order_id",
      "aggressor_side": "sell"
    }
  ]
}
```



#### ✅ 3. Test Market Orders

Place a **resting limit sell** first:

```json
{
  "symbol": "BTC-USD",
  "side": "sell",
  "order_type": "limit",
  "price": 105,
  "quantity": 1
}
```

Then submit a **market buy**:

```json
{
  "symbol": "BTC-USD",
  "side": "buy",
  "order_type": "market",
  "quantity": 1
}
```


---



## 🔍 Testing Websocket





* 📡 Monitor the live order book and trades using WebSocket clients:

  * **Order Book Feed:**

    ```bash
    npx wscat -c ws://localhost:8000/ws/book
    ```

  * **Trade Feed:**

    ```bash
    npx wscat -c ws://localhost:8000/ws/trades
    ```

  

---

### 🧪 **Tests**

Unit tests are included using **`pytest`** to verify the core matching engine logic, including:

* FIFO order matching
* Trade-through protection
* Market, Limit, IOC, FOK order handling
* Partial fills and full fills

#### ✅ To Run All Tests:

```bash
pytest test_matching.py -v
```

You can also run all test files:

```bash
pytest -v
```

> Ensure you're in the project root directory where `test_matching.py` is located.

---

### Example Output:

```bash
test_matching.py::test_limit_order_matching PASSED
test_matching.py::test_market_order_matching PASSED
test_matching.py::test_ioc_order_behavior PASSED
test_matching.py::test_fok_order_behavior PASSED
```



---

## ✅ To-Do / Improvements

* [ ] Implement Stop-Loss / Take-Profit (Bonus)
* [ ] Add persistence (save order book on shutdown)

---

## 📄 License

MIT License — Free to use, modify and distribute.

---

