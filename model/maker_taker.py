import math
from typing import Tuple
from data.orderbook import OrderBook

def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def estimate_maker_taker_proportion(
    orderbook: OrderBook,
    order_type: str,
    order_side: str,
    order_size_usd: float,
    limit_price: float = None
) -> Tuple[float, float]:
    """
    Estimate maker/taker proportion using a sigmoid approach.

    Parameters:
    - orderbook: An OrderBook instance (must be already .update()'d)
    - order_type: 'market' or 'limit'
    - order_side: 'buy' or 'sell'
    - order_size_usd: USD size of the order
    - limit_price: For limit orders, the specified limit price

    Returns:
    - (maker_proportion, taker_proportion): both in [0.0, 1.0]
    """
    asks = orderbook.get_asks()
    bids = orderbook.get_bids()
    if not asks or not bids:
        # no book data → assume evenly split
        return 0.5, 0.5

    best_ask = asks[0][0]
    best_bid = bids[0][0]
    mid_price = (best_ask + best_bid) / 2.0
    spread = max(best_ask - best_bid, 1e-8)  # avoid zero

    # 1) Market orders are pure taker
    if order_type.lower() == 'market':
        return 0.0, 1.0

    # 2) Limit orders use our sigmoid heuristic
    if order_type.lower() == 'limit' and limit_price is not None:
        # Choose the side of the book we’ll probe
        if order_side.lower() == 'buy':
            levels = asks
            ref_price = best_ask
            price_dir = 1.0
        else:  # sell
            levels = bids
            ref_price = best_bid
            price_dir = -1.0

        # a) How aggressive is the limit price?
        price_aggr = price_dir * (limit_price - ref_price) / spread

        # b) How large vs. visible liquidity?
        #    Value of top-5 levels in USD
        visible_usd = sum(p * q for p, q in levels[:5])
        size_ratio = min(1.0, order_size_usd / max(visible_usd, 1e-8))

        # c) Combine into logistic input
        #    These weights can be tuned later
        z = (
            -3.0
            + (-5.0 * price_aggr)
            + (-2.0 * size_ratio)
        )
        maker_pct = sigmoid(z)
        taker_pct = 1.0 - maker_pct
        return round(maker_pct, 4), round(taker_pct, 4)

    # 3) Fallback if we can’t decide
    return 0.5, 0.5
