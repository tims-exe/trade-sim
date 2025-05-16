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
