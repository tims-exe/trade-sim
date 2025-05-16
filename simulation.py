import asyncio
import time
from data.websocket_client import WebSocketClient
from data.orderbook import OrderBook
from model.market_impact import calculate_market_impact
from model.slippage import calculate_expected_slippage
from model.maker_taker import estimate_maker_taker_proportion
from config.settings import WEBSOCKET_URL, FEE_TIERS, ORDER_TYPE

# Configuration
EXCHANGE = "OKX"
ASSET = "BTC-USDT-SWAP"
ORDER_TYPE = "market" 
ORDER_SIZE_USD = 100
FEE_TIER = "VIP0"
VOLATILITY = 0.015  # Assumed or fetched externally

orderbook = OrderBook()

async def handle_orderbook_message(data):

    if 'bids' in data and 'asks' in data:
        start_time = time.time()

        orderbook.update(data)
        
        # 1. Expected Market Impact
        impact = calculate_market_impact(orderbook, order_type="buy", order_size_usd=ORDER_SIZE_USD, volatility=VOLATILITY)

        # 2. Slippage Estimation (Mocked or modeled with regression)
        slippage = calculate_expected_slippage(orderbook, ORDER_SIZE_USD)

        # 3. Maker/Taker Proportion
        maker_prop, taker_prop = estimate_maker_taker_proportion(
            orderbook=orderbook,
            order_type=ORDER_TYPE,
            order_side="buy",
            order_size_usd=ORDER_SIZE_USD
        )

        # 4. Fee Estimation
        fees = (
            maker_prop * ORDER_SIZE_USD * FEE_TIERS[EXCHANGE][FEE_TIER]["maker"] +
            taker_prop * ORDER_SIZE_USD * FEE_TIERS[EXCHANGE][FEE_TIER]["taker"]
        )

        # 5. Net Cost
        net_cost = slippage + impact + fees

        # 6. Internal Latency
        latency = time.time() - start_time

        # Print or log results
        print(f"\n--- Trade Simulation Output ---")
        print(f"Asset: {ASSET}")
        print(f"Order Type: {ORDER_TYPE}")
        print(f"Order Size: ${ORDER_SIZE_USD}")
        print(f"Volatility: {VOLATILITY:.4f}")
        print(f"Expected Market Impact: ${impact:.4f}")
        print(f"Expected Slippage: ${slippage:.4f}")
        print(f"Expected Fees: ${fees:.4f}")
        print(f"Maker Proportion: {maker_prop:.2%}")
        print(f"Taker Proportion: {taker_prop:.2%}")
        print(f"Net Cost: ${net_cost:.4f}")
        print(f"Internal Latency: {latency:.6f} seconds")

async def run_simulation():
    client = WebSocketClient(WEBSOCKET_URL, handle_orderbook_message)
    await client.connect()
    await client.get_data()

if __name__ == "__main__":
    asyncio.run(run_simulation())
