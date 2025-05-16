class OrderBook:
    def __init__(self):
        self.bids = []
        self.asks = []
        self.symbol = None
        self.timestamp = None
    
    def update(self, data):
        self.timestamp = data.get("timestamp")
        self.bids = [[float(price), float(size)] for price, size in data.get('bids')]
        self.asks = [[float(price), float(size)] for price, size in data.get('asks')]

        self.bids.sort(key=lambda x: x[0], reverse=True)
        self.asks.sort(key=lambda x: x[0])

    def get_asks(self):
        if not self.asks:
            return None
        return self.asks
    
    def get_bids(self):
        if not self.bids:
            return None
        return self.bids
    
    def get_mid_price(self):
        """Calculate the mid price from the best bid and ask."""
        if not self.bids or not self.asks:
            return None
        
        best_bid = self.bids[0][0]
        best_ask = self.asks[0][0]
        return (best_bid + best_ask) / 2



# class OrderBook:
#     def __init__(self):
#         self.bids = []
#         self.asks = []

#     def update(self, bids, asks):
#         self.bids = sorted(bids, key=lambda x: -float(x[0]))
#         self.asks = sorted(asks, key=lambda x: float(x[0]))

#     def top_levels(self, depth=5):
#         return {
#             "bids": self.bids[:depth],
#             "asks": self.asks[:depth]
#         }
