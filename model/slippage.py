"""
Expected Slippage (buy) = Weighted Average Execution Price - Best Ask Price

Iterate through the orderbook and check level value
"""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def calculate_expected_slippage(orderbook, order_size_usd):
    """
    Calculate expected slippage based on current orderbook.
    
    Parameters:
    - orderbook: Current orderbook with asks and bids
    - order_size_usd: Size of the order in USD
    
    Returns:
    - expected_slippage_usd: Expected slippage in USD
    """

    price_levels = orderbook.get_asks() 
    best_price = float(price_levels[0][0])
    
    remaining_order = order_size_usd
    weighted_sum = 0
    total_quantity = 0
    
    for price, qnty in price_levels:
        
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
        logger.warning("Not enough liquidity in the orderbook")
        return None

    weighted_avg_price = weighted_sum / total_quantity

    slippage = (weighted_avg_price - best_price) / best_price
    slippage_usd = slippage * order_size_usd

    return slippage_usd

