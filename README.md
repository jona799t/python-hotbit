# Python-Hotbit
A Python package for the crypto currency exchange Hotbit that doesn't require an API Key, making it available to everyone.

# Discord
Join click [here](https://discord.gg/FAK6yVQFE3) to join our Discord

# Documentation
This package is still at the developement stage which is why not all endpoints are covered.

## Auth
### Email, Password, 2FA
```python
import hotbit

email = "myemail@email.com"
password = "MyPassword"
authenticatorCode = "MyAuthenticatorCode"

captchaKey = "My 2Captcha Key or Anti-Captcha Key"

auth = hotbit.auth.login(email=email, password=password, authenticatorCode=authenticatorCode, antiCaptcha=captchaKey)
Client = hotbit.Hotbit(auth)
```
### Official API (Key/Secret)
If you want help gaining access to the official api, join the [Discord](https://discord.gg/hotbit).
```python
import hotbit

auth = hotbit.auth.api(api_key="My API Key", api_secret="My API Secret")
client = hotbit.Hotbit(auth)
```  
### Cookie
```python
import hotbit

auth = hotbit.auth.cookie(cookies="My Cookie String")
client = hotbit.Hotbit(auth)
```  
  
  

## Hotbit
### Server Time
Get the server time of Hotbit
```python
client.serverTime()
```

### Place Order
Buy/sell something
```python
price = 1.012

client.order(market="ADA/USDT", side="BUY", amount=10, price=0.6)
```

### Cancel Order
Cancel a select order
```python
client.cancelOrder(market="ADA/USDT", order_id="4365873")
```

### Balance Query
Query your balance on Hotbit
```python
client.balanceQuery()
```

### Price
Retreve the price of a select market
```python
market = "ADA/USDT"
client.price(market)
```

### Market Price
Retreve the instant buy/sell price of a select market.  
This function has some logic behind it meaning it does not only use Hotbit's endpoints to calculate.
```python
market = "ADA/USDT"
side = "BUY"
amount = 1000 # USDT (Last part of market)

client.price(market=market, side=side, amount=amount)
```

### Depth Query
Query ask and bid prices and amount
```python
market = "ADA/USDT"
client.depthQuery(market)
```

### Market List
Retreve a list over all markets
```python
client.serverTime()
```

### Allticker
Retreve a list over all tickers
```python
client.serverTime()
```

### HTTP
This only works when using the official API. Endpoints can be found here: https://hotbitex.github.io/slate/docs/spot/v2/en
```python
urlPath = "/p2/balance.query"
payload = 'assets=[]'

client.http(urlPath, payload).json()
```
