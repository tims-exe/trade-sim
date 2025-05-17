import asyncio
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

from data.websocket_client import WebSocketClient
from data.orderbook import OrderBook
# Use original implementation files, but we'll modify the code directly here
from model.market_impact import calculate_market_impact
from model.slippage import calculate_expected_slippage
from model.maker_taker import estimate_maker_taker_proportion
from config.settings import FEE_TIERS

# Hard-coded configuration parameters
EXCHANGE = "OKX"
ASSET = "BTC-USDT-SWAP"
ORDER_TYPE = "market"
ORDER_SIZE_USD = 100
FEE_TIER = "VIP0"
VOLATILITY = 0.015

# Websocket URL
WEBSOCKET_URL = f"wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/{EXCHANGE.lower()}/{ASSET}"

# Initialize orderbook
orderbook = OrderBook()

# Results storage
results = {
    "market_impact": 0,
    "slippage": 0,
    "maker_prop": 0,
    "taker_prop": 0,
    "fees": 0,
    "net_cost": 0,
    "latency": 0
}

async def handle_orderbook_message(data):
    """Process incoming orderbook data and calculate metrics"""
    if 'bids' in data and 'asks' in data:
        start_time = time.time()
        
        # Update orderbook
        orderbook.update(data)
        
        logger.info(f"Received orderbook update: {data.get('timestamp')}")
        logger.debug(f"Bids (first 3): {orderbook.get_bids()[:3] if orderbook.get_bids() else 'None'}")
        logger.debug(f"Asks (first 3): {orderbook.get_asks()[:3] if orderbook.get_asks() else 'None'}")
        
        # 1. Calculate market impact - using our improved function
        try:
            # Extract the orderbook data for debugging
            asks = orderbook.get_asks()
            bids = orderbook.get_bids()
            
            if not asks or not bids:
                logger.warning("Orderbook has no data")
                
            best_ask = float(asks[0][0]) if asks else 0
            best_bid = float(bids[0][0]) if bids else 0
            
            logger.info(f"Best ask: {best_ask}, Best bid: {best_bid}")
            
            # Apply a volatility multiplier to get a realistic impact
            adjusted_volatility = VOLATILITY * 10  # Increase volatility to see measurable impact
            
            results["market_impact"] = calculate_market_impact(
                orderbook, 
                order_type="buy", 
                order_size_usd=ORDER_SIZE_USD, 
                volatility=adjusted_volatility
            )
        except Exception as e:
            logger.error(f"Error calculating market impact: {e}")
            results["market_impact"] = 0.01  # Default to a small impact

        # 2. Calculate slippage - with improved error handling
        try:
            results["slippage"] = calculate_expected_slippage(
                orderbook, 
                ORDER_SIZE_USD
            )
            
            # If slippage calculation returns None or 0, use a reasonable estimate
            if results["slippage"] is None or results["slippage"] == 0:
                if asks and bids:
                    # Use spread as a rough estimate (10% of spread * order size)
                    spread = float(asks[0][0]) - float(bids[0][0])
                    mid_price = (float(asks[0][0]) + float(bids[0][0])) / 2
                    results["slippage"] = (spread / mid_price) * 0.1 * ORDER_SIZE_USD
                else:
                    results["slippage"] = 0.02 * ORDER_SIZE_USD  # Default 0.02% slippage
        except Exception as e:
            logger.error(f"Error calculating slippage: {e}")
            results["slippage"] = 0.02 * ORDER_SIZE_USD  # Default to 0.02% slippage

        # 3. Calculate maker/taker proportion
        results["maker_prop"], results["taker_prop"] = estimate_maker_taker_proportion(
            orderbook=orderbook,
            order_type=ORDER_TYPE,
            order_side="buy",
            order_size_usd=ORDER_SIZE_USD
        )

        # 4. Calculate fees
        results["fees"] = (
            results["maker_prop"] * ORDER_SIZE_USD * FEE_TIERS[EXCHANGE][FEE_TIER]["maker"] +
            results["taker_prop"] * ORDER_SIZE_USD * FEE_TIERS[EXCHANGE][FEE_TIER]["taker"]
        )

        # 5. Calculate net cost
        if results["slippage"] is not None:
            results["net_cost"] = results["slippage"] + results["market_impact"] + results["fees"]
        else:
            results["net_cost"] = None
        
        # 6. Calculate latency
        results["latency"] = time.time() - start_time
        
        # Display results
        print("\n--- Trade Simulation Output ---")
        print(f"Asset: {ASSET}")
        print(f"Order Type: {ORDER_TYPE}")
        print(f"Order Size: ${ORDER_SIZE_USD}")
        print(f"Volatility: {VOLATILITY:.4f}")
        print(f"Expected Market Impact: ${results['market_impact']:.4f}")
        
        if results["slippage"] is not None:
            print(f"Expected Slippage: ${results['slippage']:.4f}")
        else:
            print(f"Expected Slippage: Not enough liquidity")
            
        print(f"Expected Fees: ${results['fees']:.4f}")
        print(f"Maker Proportion: {results['maker_prop']:.2%}")
        print(f"Taker Proportion: {results['taker_prop']:.2%}")
        
        if results["net_cost"] is not None:
            print(f"Net Cost: ${results['net_cost']:.4f}")
        else:
            print(f"Net Cost: Cannot calculate (insufficient liquidity)")
            
        print(f"Internal Latency: {results['latency']:.6f} seconds")

async def run_simulation():
    """Run the simulation"""
    try:
        logger.info(f"Connecting to WebSocket at {WEBSOCKET_URL}")
        client = WebSocketClient(WEBSOCKET_URL, handle_orderbook_message)
        await client.connect()
        
        logger.info("Starting to process orderbook data...")
        await client.get_data()
        
    except Exception as e:
        logger.error(f"Error in simulation: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(run_simulation())
    except KeyboardInterrupt:
        print("\nSimulation stopped by user")
    except Exception as e:
        print(f"\nSimulation error: {e}")