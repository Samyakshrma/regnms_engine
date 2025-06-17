from app.models import Order, Trade
from app.order_book import OrderBook
from app.utils import generate_id, current_timestamp
from typing import List

class MatchingEngine:
    def __init__(self):
        self.order_book = OrderBook()
        self.trades: List[Trade] = []

    def match_order(self, order: Order):
        remaining_qty = order.quantity
        trades = []

        if order.order_type == "fok":
            # Dry run to simulate fill
            simulated_qty = 0
            test_qty = remaining_qty
            simulated_trades = []
            temp_order_book = self.order_book.clone()

            while test_qty > 0:
                best_price, best_order = temp_order_book.get_best_price_order(order.side)
                if not best_order:
                    break

                is_match = (
                    order.side == "buy" and order.price >= best_price or
                    order.side == "sell" and order.price <= best_price
                )

                if not is_match:
                    break

                fill_qty = min(test_qty, best_order.quantity)
                simulated_qty += fill_qty
                test_qty -= fill_qty
                best_order.quantity -= fill_qty

                if best_order.quantity == 0:
                    temp_order_book.cancel_order(best_order.id)

            if simulated_qty < order.quantity:
                return []  # Cannot fully fill → kill entire order

        # Main matching loop
        while remaining_qty > 0:
            best_price, best_order = self.order_book.get_best_price_order(order.side)
            if not best_order:
                break

            is_match = (
                order.order_type == "market" or
                (order.side == "buy" and order.price >= best_price) or
                (order.side == "sell" and order.price <= best_price)
            )

            if not is_match:
                break

            traded_qty = min(remaining_qty, best_order.quantity)
            trade = Trade(
                trade_id=generate_id(),
                symbol=order.symbol,
                price=best_price,
                quantity=traded_qty,
                timestamp=current_timestamp(),
                maker_order_id=best_order.id,
                taker_order_id=order.id,
                aggressor_side=order.side
            )
            trades.append(trade)
            self.trades.append(trade)

            remaining_qty -= traded_qty
            best_order.quantity -= traded_qty

            if best_order.quantity == 0:
                self.order_book.cancel_order(best_order.id)

        # Handle post-match behavior
        if remaining_qty > 0:
            if order.order_type == "limit":
                order.quantity = remaining_qty
                self.order_book.add_order(order)
            elif order.order_type == "ioc":
                pass  # Unfilled qty is canceled
            elif order.order_type == "fok":
                # Should not happen — covered by pre-check
                pass

        return trades
