# Settings for the trade simulator

# WebSocket URL for L2 orderbook data
WEBSOCKET_URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

FEE_TIERS = {
    "OKX": {
        "VIP0": {"maker": 0.0008, "taker": 0.0010},
        "VIP1": {"maker": 0.0006, "taker": 0.0008},
        "VIP2": {"maker": 0.0004, "taker": 0.0006},
    }
}

# Available exchanges
EXCHANGES = ["OKX"]

# Default order type
ORDER_TYPE = "market"