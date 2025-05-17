def calculate_market_impact(orderbook, order_type, order_size_usd, volatility = None):
    """
    Calculate the market impact of an order using the Almgren-Chriss model.
    
    Parameters:
    - orderbook: Current orderbook with asks and bids
    - order_type: 'buy' or 'sell'
    - order_size_usd: Size of the order in USD
    - volatility: Optional volatility parameter
    
    Returns:
    - market_impact_usd: Market impact in USD
    """
    asks = orderbook.get_asks()
    bids = orderbook.get_bids()

    if not bids or not asks:
        return 0

    best_ask = float(asks[0][0])
    best_bid = float(bids[0][0])
    mid_price = (best_bid + best_ask) / 2
    
    if mid_price <= 0:
        return 0

    # Normalized spread
    spread = (best_ask - best_bid) / mid_price
    
    # Orderbook imbalance (Top 5 levels)
    bid_volume = sum(float(qty) for _, qty in bids[:5])
    ask_volume = sum(float(qty) for _, qty in asks[:5])

    total_volume = bid_volume + ask_volume
    if total_volume <= 0:
        return 0
    
    # Determine imbalance factor based on order type
    if order_type.lower() == 'buy':
        imbalance_ratio = ask_volume / total_volume  # Higher ratio means less liquidity on ask side
    else:
        imbalance_ratio = bid_volume / total_volume  # Higher ratio means less liquidity on bid side
    
    imbalance_factor = 0.5 + (0.5 * (1 - imbalance_ratio))  # Scale between 0.5 and 1

    # Convert order size to base units
    order_size_base = order_size_usd / mid_price

    # Rough estimate of daily volume
    estimated_daily_volume_base = total_volume * 100  # Multiplier can be adjusted

    # Estimate volatility if not provided
    if volatility is None or volatility <= 0:
        volatility = max(0.01, spread * 10)  # Ensure minimal volatility

    # Market impact calculation (Almgren-Chriss style)
    beta = 0.6  # power-law exponent
    market_impact_constant = 0.1  # Constant factor to ensure impact is measurable
    
    if estimated_daily_volume_base <= 0:
        return 0
        
    relative_size = order_size_base / estimated_daily_volume_base
    market_impact_percent = market_impact_constant * volatility * (relative_size ** beta) * spread * imbalance_factor
    market_impact_usd = market_impact_percent * order_size_usd

    #print(f"\n\n===========================================REacehd {market_impact_usd}\n\n")

    return max(0.0, market_impact_usd)  # Ensure non-negative impact