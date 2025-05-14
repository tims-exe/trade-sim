import asyncio
import websockets
import json

# WebSocket URL
WS_URL = "wss://ws.gomarket-cpp.goquant.io/ws/l2-orderbook/okx/BTC-USDT-SWAP"

async def receive_full_orderbook():
    async with websockets.connect(WS_URL) as websocket:
        print("Connected to WebSocket\n")

        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)

                print(json.dumps(data, indent=2))

                # # Reformat the data to match your required structure
                # formatted_data = {
                #     "timestamp": data.get("timestamp"),
                #     "exchange": data.get("exchange"),
                #     "symbol": data.get("symbol"),
                #     "asks": data.get("asks", []),
                #     "bids": data.get("bids", [])
                # }

                # print(json.dumps(formatted_data, indent=2))


            except Exception as e:
                print("Error:", e)

asyncio.run(receive_full_orderbook())
