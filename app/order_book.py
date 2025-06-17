from collections import deque
from sortedcontainers import SortedDict
from typing import Dict, List
from app.models import Order
from copy import deepcopy

class OrderBook:
    def __init__(self):
        self.bids = SortedDict(lambda x: -x)  # Highest price first
        self.asks = SortedDict()  # Lowest price first

    def add_order(self, order: Order):
        book = self.bids if order.side == "buy" else self.asks
        if order.price not in book:
            book[order.price] = deque()
        book[order.price].append(order)

    def cancel_order(self, order_id: str):
        for book in [self.bids, self.asks]:
            for price in list(book.keys()):
                queue = book[price]
                book[price] = deque([o for o in queue if o.id != order_id])
                if not book[price]:
                    del book[price]

    def top_levels(self, side: str, depth: int = 10):
        book = self.bids if side == "buy" else self.asks
        return [[price, sum(o.quantity for o in orders)] for price, orders in list(book.items())[:depth]]

    def get_best_price_order(self, side: str):
        book = self.asks if side == "buy" else self.bids
        if not book:
            return None, None
        price = next(iter(book))
        order = book[price][0]
        return price, order

    def clone(self):
        clone_book = OrderBook()
        # Deepcopy both bids and asks
        clone_book.bids = SortedDict(self.bids.key)
        for price, queue in self.bids.items():
            clone_book.bids[price] = deque(deepcopy(queue))
        
        clone_book.asks = SortedDict()
        for price, queue in self.asks.items():
            clone_book.asks[price] = deque(deepcopy(queue))
        
        return clone_book
