import math
from typing import Tuple

def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def estimate_maker_taker_proportion(orderbook, order_type, order_side, order_size_usd, limit_price = None):
    asks = orderbook.get_asks()
    bids = orderbook.get_bids()
    if not asks or not bids:
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
        if order_side.lower() == 'buy':
            levels = asks
            ref_price = best_ask
            price_dir = 1.0
        else:  # sell
            levels = bids
            ref_price = best_bid
            price_dir = -1.0

        price_aggr = price_dir * (limit_price - ref_price) / spread

        visible_usd = sum(p * q for p, q in levels[:5])
        size_ratio = min(1.0, order_size_usd / max(visible_usd, 1e-8))

        z = (
            -3.0
            + (-5.0 * price_aggr)
            + (-2.0 * size_ratio)
        )
        maker_pct = sigmoid(z)
        taker_pct = 1.0 - maker_pct
        return round(maker_pct, 4), round(taker_pct, 4)

    return 0.5, 0.5
