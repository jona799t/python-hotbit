import hashlib
import requests
import requestsWS


class Hotbit:
    def __init__(self, apiKey, apiSecret):
        self.baseUrl = "https://api.hotbit.io/v2"

        self.api_key = apiKey
        self.api_secret = apiSecret

        self.sessionWS = requestsWS.Session()

    def http(self, urlpath, payload, type="GET"):
        if urlpath.split("/")[1] == "p2":
            payload = f"api_key={self.api_key}&{payload}"
            signature = hashlib.md5(f"{payload}&secret_key={self.api_secret}".encode()).hexdigest().upper()
            payload = f"?{payload}&sign={signature}"

        if type == "POST":
            return requests.post(self.baseUrl + urlpath + payload)
        return requests.get(self.baseUrl + urlpath + payload)

    
    def serverTime(self):
        return self.http("/p1/server.time", '').json()

    def balanceQuery(self):
        return self.http("/p2/balance.query", 'assets=[]').json()

    def depthQuery(self, market, interval="0.0000000001", limit=100):
        payload = {
            "method":"depth.query",
            "params":[market.replace("/", ""),limit,interval],
            "id":100
        }
        return self.sessionWS.post("wss://ws.hotbit.io/v2/", json=payload, encryption="gzip", identifiers={"id": 100}).json()

    def marketPrice(self, market, side, amount=0):
        resp = self.depthQuery(market)
        if side.lower() == "buy":
            asks = resp["result"]["asks"]
            _amount = 0
            for ask in asks:
                if ask == None:
                    break
                _amount += float(ask[0]) * float(ask[1])
                if _amount >= amount:
                    sellPrice = ask[0]
                    break

            return sellPrice
        elif side.lower() == "sell":
            bids = resp["result"]["bids"]
            _amount = 0
            for bid in bids:
                if bid == None:
                    break
                _amount += float(bid[0]) * float(bid[1])
                if _amount >= amount:
                    buyPrice = bid[0]
                    break

            return buyPrice
        else:
            exit(f"Hotbit API | Side has to be either buy or sell")

    def marketList(self):
        return self.http("/p1/market.list", f'').json()

    def allticker(self):
        return self.http("/p1/allticker", f'').json()

    def cancelOrder(self, market, order_id):
        return self.http("/p2/order.cancel", f"market={market.upper()}&order_id={order_id}").json()

    def order(self, market, side, amount, price, isfee=1):
        try:
            if side.upper() == "SELL":
                side = 1
            elif side.upper() == "BUY":
                side = 2
        except Exception:
            pass
        print(f"market={market.upper()}&side={side}&amount={amount}&price={price}&isfee={isfee}")
        return self.http("/p2/order.put_limit", f"market={market.upper()}&side={side}&amount={amount}&price={price}&isfee={isfee}", type="POST").json()