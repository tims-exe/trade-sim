import logging

def calculate_expected_slippage(orderbook, order_size_usd, order_side="buy"):
    """
    Calculate expected slippage based on current orderbook.
    
    Parameters:
    - orderbook: Current orderbook with asks and bids
    - order_size_usd: Size of the order in USD
    - order_side: 'buy' or 'sell'
    
    Returns:
    - expected_slippage_usd: Expected slippage in USD
    """
    # Select the appropriate price levels based on order side
    if order_side.lower() == "buy":
        price_levels = orderbook.get_asks()
        if not price_levels:
            return None
        best_price = float(price_levels[0][0])
    else:  # sell
        price_levels = orderbook.get_bids()
        if not price_levels:
            return None
        best_price = float(price_levels[0][0])
    
    remaining_order = order_size_usd
    weighted_sum = 0
    total_quantity = 0
    
    for price, qnty in price_levels:
        price = float(price)
        qnty = float(qnty)
        
        level_value = price * qnty

        if remaining_order <= level_value:
            # we only need a portion of this level
            qnty_needed = remaining_order / price
            weighted_sum += qnty_needed * price
            total_quantity += qnty_needed
            remaining_order = 0
            break
        else:
            # use this entire level and continue
            weighted_sum += qnty * price
            total_quantity += qnty
            remaining_order -= level_value
    
    if remaining_order > 0:
        logging.warning(f"Not enough liquidity in the orderbook for {order_size_usd} USD order")
        # For small amounts, let's be optimistic and return a small slippage rather than None
        if total_quantity > 0:
            weighted_avg_price = weighted_sum / total_quantity
            slippage = abs(weighted_avg_price - best_price) / best_price
            return slippage * order_size_usd
        return None

    weighted_avg_price = weighted_sum / total_quantity if total_quantity > 0 else best_price
    
    # For buy orders: slippage is how much higher the avg price is than best price
    # For sell orders: slippage is how much lower the avg price is than best price
    if order_side.lower() == "buy":
        slippage = (weighted_avg_price - best_price) / best_price
    else:
        slippage = (best_price - weighted_avg_price) / best_price
        
    slippage_usd = slippage * order_size_usd

    #print(f"\n\n===========================================REacehd slip {slippage}\n\n")

    
    return max(0.0, slippage_usd)  # Ensure we don't return negative slippage