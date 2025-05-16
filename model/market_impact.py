def calculate_market_impact(orderbook, order_type, order_size_usd, volatility = None):
    
    asks = orderbook.get_asks()
    bids = orderbook.get_bids()

    if not bids or not asks:
        return 0

    best_ask = asks[0][0]
    best_bid = bids[0][0]
    mid_price = (best_bid + best_ask) / 2

    # Normalized spread
    spread = (best_ask - best_bid) / mid_price

    # Orderbook imbalance (Top 5 levels)
    bid_volume = sum(qty for _, qty in bids[:5])
    ask_volume = sum(qty for _, qty in asks[:5])

    total_volume = bid_volume + ask_volume
    if total_volume == 0:
        imbalance_factor = 1.0
    else:
        if order_type == 'buy':
            imbalance_ratio = bid_volume / total_volume
        else:
            imbalance_ratio = ask_volume / total_volume
        imbalance_factor = 0.5 + imbalance_ratio 

    # Convert order size to base units (e.g., BTC)
    order_size_base = order_size_usd / mid_price

    # Rough estimate of daily volume
    estimated_daily_volume_base = total_volume * 100 

    # Estimate volatility if not provided
    if volatility is None:
        volatility = spread * 10

    # Market impact calculation (Almgren-Chriss style)
    beta = 0.6  # power-law exponent
    relative_size = order_size_base / estimated_daily_volume_base
    market_impact_percent = volatility * (relative_size ** beta) * spread * imbalance_factor
    market_impact_usd = market_impact_percent * order_size_usd

    return market_impact_usd
