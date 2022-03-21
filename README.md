# Python-Hotbit
A Python package for the cryptocurrency exchange Hotbit that doesn't require an API Key, making it available to everyone.

This package is still at the development stage which is why not all endpoints are covered.

# Discord
Join click [here](https://discord.gg/FAK6yVQFE3) to join our Discord.

# Documentation
## Auth
### Email, Password, 2FA
For this method the either [Anti-Captcha](https://anti-captcha.com/) or [2Captcha](https://2captcha.com/) is needed  
Please notice the price of login is about **$0.0019** on **Anti-Captcha** and about **$0.0029** on **2Captcha**, as they charge for the captcha solving.  
If you don't want to pay you can use either **Key/Secret** or **Cookie** as the authorization method.
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
Get the server time of Hotbit.
```python
client.serverTime()
```

### Place Order
Buy/sell something.
```python
client.order(market="ADA/USDT", side="BUY", amount=10, price=0.6)
```

### Cancel Order
Cancel a select order.
```python
client.cancelOrder(market="ADA/USDT", order_id="4365873")
```

### Balance Query
Query your balance on Hotbit.
```python
client.balanceQuery()
```

### Market Price
Retrieve the instant buy/sell price of a select market.  
This function has some logic behind it meaning it does not only use Hotbit's endpoints to calculate.
```python
market = "ADA/USDT"
side = "BUY"
amount = 1000 # USDT (Last part of market)

client.price(market=market, side=side, amount=amount)
```

### Depth Query
Query ask and bid prices and amount.
```python
market = "ADA/USDT"
client.depthQuery(market)
```

### Market List
Retrieve a list of all markets.
```python
client.marketList()
```

### Allticker
Retreve a list over all tickers.
```python
client.allticker()
```

### HTTP
This only works when using the official API. Endpoints can be found here: https://hotbitex.github.io/slate/docs/spot/v2/en.
```python
urlPath = "/p2/balance.query"
payload = 'assets=[]'

client.http(urlPath, payload).json()
```
