import requests
import requestsWS
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from decimal import *

def round_down(value, decimals): # https://stackoverflow.com/questions/41383787/round-down-to-2-decimal-in-python
    with localcontext() as ctx:
        ctx.rounding = ROUND_DOWN
        return round(value, decimals)

class Hotbit:
    def __init__(self, auth):
        # create session and WS session
        ## create driver with selenium/undetected_chromedriver
        print("Solving Cloudflare - allow up to 5s")
        driver = uc.Chrome()
        driver.implicitly_wait(15)
        driver.get("https://www.hotbit.io/")
        driver.find_element(By.XPATH, '/html/body/div[1]/div[1]/div[1]/div/div[1]/p[1]')  # waits till cf is solved and the Hotbit Title is visable

        ## get cookies and user_agent
        brCookies = driver.get_cookies()
        ua = driver.execute_script("return navigator.userAgent")

        ## filter out the cf_clearance cookie
        cf_cookie = [cookie for cookie in brCookies if cookie['name'] == 'cf_clearance'][0]['value']
        self.cookies = {"cf_clearance": cf_cookie}
        self.defaultHeaders = {"user-agent": ua}
        driver.close()
        print('Successfully solved Cloudflare')

        self.session = requests.Session()
        self.sessionWS = requestsWS.Session()

        # add cf and hotbit-account cookies
        for key, value in auth.items():
            self.session.cookies.set(key, value, domain="hotbit.io")

        # set defaultHeader, cookies, check status of first get request and assign params for openingPayload
        self.session.headers['User-Agent'] = ua
        self.session.headers['referer'] = 'https://www.hotbit.io/dw'
        resp = self.session.get('https://www.hotbit.io/v1/info?platform=web', headers=self.defaultHeaders, cookies=self.cookies)

        if resp.json()['Msg'] != 'success' or resp.status_code != 200:
            print(resp.content)
            exit(resp.status_code)

        whereFrom = resp.json()["Content"]["user_sign"]["from"]
        sign = resp.json()["Content"]["user_sign"]["sign"]
        time = resp.json()["Content"]["user_sign"]["time"]
        self.uid = resp.json()["Content"]["user_sign"]["uid"]

        self.openingPayload = {
            "id": 300,
            "method": "server.auth2",
            "params": [self.uid, time, whereFrom, sign]
        }
        self.wsPost('wss://ws.hotbit.io/', self.sessionWS, json=self.openingPayload, encryption="gzip", identifiers={"id": 300})

        payload = {
            "method": "server.ping",
            "params": [],
            "id": 104
        }
        self.sessionWS.keepConnection('wss://ws.hotbit.io/', interval=20, json=payload)

        self.marketPrecision = {}
        for market in self.marketList():
            self.marketPrecision[market["name"]] = market["money_prec"]


    def wsGet(self, wsUrl, session, headers={}, encryption=None, identifiers=None, timeout=None, debug=False):
        try:
            return session.get(wsUrl, headers=headers, encryption=encryption, identifiers=identifiers, timeout=timeout, debug=debug)
        except Exception:
            session.wsData = {"CURRENT_URL": None}
            session.post('wss://ws.hotbit.io/', json=self.openingPayload, encryption="gzip", identifiers={"id": 300})
            return session.post(wsUrl, headers=headers, encryption=encryption, data=data, json=json, waitForResponse=waitForResponse, identifiers=identifiers, timeout=timeout, debug=debug)

    def wsPost(self, wsUrl, session, headers={}, encryption=None, data=None, json=None, waitForResponse=True, identifiers=None, timeout=None, debug=False):
        try:
            return session.post(wsUrl, headers=headers, encryption=encryption, data=data, json=json, waitForResponse=waitForResponse, identifiers=identifiers, timeout=timeout, debug=debug)
        except Exception:
            session.wsData = {"CURRENT_URL": None}
            session.post('wss://ws.hotbit.io/', json=self.openingPayload, encryption="gzip", identifiers={"id": 300})
            return session.post(wsUrl, headers=headers, encryption=encryption, data=data, json=json, waitForResponse=waitForResponse, identifiers=identifiers, timeout=timeout, debug=debug)

    def serverTime(self):
        payload = {
            "method": "server.time",
            "params": [],
            "id": 10
        }
        resp = self.wsPost('wss://ws.hotbit.io/', self.sessionWS, json=payload, encryption="gzip", identifiers={"id": 10})
        return resp.json()

    def stateSubscribeall(self, receiver):
        payload = {
            "method": "state.subscribeall",
            "params": [],
            "id": 402
        }
        self.wsPost('wss://ws.hotbit.io/', self.sessionWS, json=payload, encryption="gzip", waitForResponse=False)

        while True:
            resp = self.wsGet('wss://ws.hotbit.io/', self.sessionWS, encryption="gzip", identifiers={"id": 0})
            receiver(resp.json())

    def balanceQuery(self):
        payload = {
            "id": 405,
            "method": "balance.query",
            "params": []
        }
        resp = self.wsPost('wss://ws.hotbit.io/', self.sessionWS, json=payload, encryption="gzip", identifiers={"id": 405})
        return resp.json()

    def depthQuery(self, market, interval="1e-8", limit=100):
        market = market.replace("/", "")
        payload = {
            "method": "depth.query",
            "params": [
                market,
                limit,
                interval
            ],
            "id": 20
        }
        resp = self.wsPost('wss://ws.hotbit.io/', self.sessionWS, json=payload, encryption="gzip", identifiers={"id": 20})
        return resp.json()

    def orderQuery(self, offset=0, limit=50):
        payload = {
            "method": "order.query",
            "params": [
                [],
                offset,
                limit
            ],
            "id": 13
        }
        resp = self.wsPost('wss://ws.hotbit.io/', self.sessionWS, json=payload, encryption="gzip", identifiers={"id": 13})
        return resp.json()

    def marketPrice(self, market, side, amount=0):
        market = market.replace("/", "")
        payload = {
            "method": "depth.query",
            "params": [
                market,
                100,
                "1e-8"
            ],
            "id": 20
        }
        resp = self.wsPost('wss://ws.hotbit.io/', self.sessionWS, json=payload, encryption="gzip", identifiers={"id": 20})
        if side.lower() == "buy":
            asks = resp.json()["result"]["asks"]
            _amount = 0
            for ask in asks:
                if ask == None:
                    break
                _amount += float(ask[0]) * float(ask[1])
                if _amount >= amount:
                    sellPrice = ask[0]
                    break

            return float(round_down(Decimal(sellPrice), self.marketPrecision[market]))
        elif side.lower() == "sell":
            bids = resp.json()["result"]["bids"]
            _amount = 0
            for bid in bids:
                if bid == None:
                    break
                _amount += float(bid[0]) * float(bid[1])
                if _amount >= amount:
                    buyPrice = bid[0]
                    break

            return float(round_down(Decimal(buyPrice), self.marketPrecision[market]))
        else:
            exit(f"Hotbit API | Side has to be either buy or sell")

    def marketList(self):
        resp = self.session.get("https://api.hotbit.io/api/v1/market.list")
        if resp.json()["error"] != None:
            print(resp.content)
            exit(resp.status_code)
        return resp.json()["result"]

    def allticker(self):
        resp = self.session.get("https://api.hotbit.io/api/v1/allticker")
        return resp.json()["ticker"]

    def cancelOrder(self, market, order_id):
        market = market.replace("/", "")
        payload = {
            "market": market.upper(),
            "order_id": order_id
        }
        resp = self.session.post("https://www.hotbit.io/v1/order/cancel?platform=web", headers=self.defaultHeaders, data=payload, cookies=self.cookies)
        return resp.json()

    def order(self, price, amount, market, side, type="LIMIT", hide=False, use_discount=False):
        asks = self.depthQuery(market)["result"]["asks"]
        decimals = 0
        for ask in asks[:2]:
            if "." in ask[1]:
                decimals = len(ask[1].split(".")[1])

        payload = {
            "price": price,
            "quantity": round_down(amount, decimals),
            "market": market,
            "side": side.upper(),
            "type": type.upper(),
            "hide": hide,
            "use_discount": use_discount
        }
        resp = self.session.post("https://www.hotbit.io/v1/order/create?platform=web", headers=self.defaultHeaders, cookies=self.cookies, data=payload)
        return resp.json()
    
    def priceQuery(self, market):
        market = market.replace("/", "")

        payload = {
            "method":"price.query",
            "params":[market],
            "id":100
        }

        resp = self.sessionWS.post(
            'wss://ws.hotbit.io/',
            json=payload,
            encryption="gzip",
            identifiers={"id": 100}
        )
        return resp.json()

    def fetchTradeHistory(self, market, limit, last_id=0):
        payload = {
            "market": market,
            "limit": limit,
            "last_id": last_id
        }
        resp = self.session.post(f'https://api.hotbit.io/api/v1/market.deals?market={market}&limit={limit}&last_id={last_id}', data=payload, headers=self.defaultHeaders, cookies=self.cookies)
        return resp.json()

    def customWS(self, whatToSend):
        resp = self.wsPost('wss://ws.hotbit.io/', self.sessionWS, json=whatToSend, encryption="gzip").text
        return resp

    def customHTTP(self, url, whatToSend):
        resp = self.session.post(url, json=whatToSend).text
        return resp
