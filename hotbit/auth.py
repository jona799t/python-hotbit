import base64
from anticaptchaofficial.geetestproxyless import * #import requests
from twocaptcha import TwoCaptcha
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5 as Cipher_PKCS1_v1_5

def _(status):
    pass

def login(email="", password="", phone="", authenticatorCode="", antiCaptcha=None, twoCaptcha=None, logger=_):
    if password == "":
        exit("Hotbit API | Please remember a password")
    elif email == "" and phone == "":
        exit("Hotbit API | Please remember an email or phone")
    elif antiCaptcha == None and twoCaptcha == None:
        exit("Hotbit API | Please remember either a captcha key or a cookie")

    session = requests.session()

    session.get("http://hotbit.pro/")

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "da-DK,da;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "no-cache",
        "pragma": "no-cache",
        "referer": "https://www.hotbit.pro/",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sec-gpc": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36",
    }
    resp = session.get("https://www.hotbit.pro/v1/info?platform=web", headers=headers)
    if resp.status_code != 200 or resp.json()["Msg"] != "success":
        print(resp.content)
        exit(resp.status_code)
    pkeyBase64 = base64.b64decode(resp.json()["Content"]["pkey"].encode()).decode()
    pkey = RSA.importKey(pkeyBase64)
    cipher = Cipher_PKCS1_v1_5.new(pkey)

    email = base64.b64encode(cipher.encrypt(
        email.encode())).decode()
    phone = base64.b64encode(cipher.encrypt(
        phone.encode())).decode()
    password = base64.b64encode(cipher.encrypt(password.encode())).decode()
    if authenticatorCode:
        authenticatorCode = base64.b64encode(cipher.encrypt(authenticatorCode.encode())).decode()

    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-DK,en;q=0.9,da-DK;q=0.8,da;q=0.7,en-US;q=0.6',
        'referer': 'https://www.hotbit.pro/login',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    }
    resp = session.get("https://www.hotbit.pro/v1/security/gtcode?source=web&scene=login&platform=web", headers=headers)
    if resp.status_code != 200:
        print(resp.content)
        exit(resp.status_code)

    logger("Solving captcha")

    # Brug 2Captcha, anti-captcha, puppeteer, eller andet til GeeTest
    if antiCaptcha:
        solver = geetestProxyless()
        solver.set_key(antiCaptcha)
        solver.set_website_url("https://www.hotbit.pro/")
        solver.set_gt_key(resp.json()["Content"]["captcha_id"])
        solver.set_challenge_key(resp.json()["Content"]["challenge"])

        result = solver.solve_and_return_solution()
        if result == 0:
            exit(f"task finished with error {solver.error_code}")

        geetest_challenge = result["challenge"]
        geetest_validate = result["validate"]
        geetest_seccode = result["seccode"]
    elif twoCaptcha:
        solver = TwoCaptcha(twoCaptcha)
        result = solver.geetest(gt=resp.json()["Content"]["captcha_id"],
                                challenge=resp.json()["Content"]["challenge"],
                                url='https://www.hotbit.pro/')

        geetest_challenge = result["code"]["geetest_challenge"]
        geetest_validate = result["code"]["geetest_validate"]
        geetest_seccode = result["code"]["geetest_seccode"]

    logger("Captcha solved")

    library = {
        "+": "%2B",
        "/": "%2F",
        "=": "%3D",
        "|": "%7C"
    }

    def format(string):
        for key, value in library.items():
            string = string.replace(key, value)
        return string

    payload = \
        "type=1&" \
        f"email={format(email)}&" \
        f"phone={format(phone)}&" \
        f"captcha={format(authenticatorCode)}&" \
        f"password={format(password)}&" \
        f"geetest_challenge={format(geetest_challenge)}&" \
        f"geetest_validate={format(geetest_validate)}&" \
        f"geetest_seccode={format(geetest_seccode)}&" \
        "geetest_success=1&" \
        "source=web&" \
        "scene=login"

    logger("Logging in ...")
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-DK,en;q=0.9,da-DK;q=0.8,da;q=0.7,en-US;q=0.6',
        'client': '1',
        'content-length': str(len(payload)),
        'content-type': 'application/x-www-form-urlencoded',
        'origin': 'https://www.hotbit.pro',
        'referer': 'https://www.hotbit.pro/login',
        'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    }
    session.post("https://www.hotbit.pro/v1/account/login?platform=web", headers=headers, data=payload)

    return session.cookies.get_dict()


def cookie(cookies):
    if type(cookies) == dict:
        pass
    elif type(cookies) == str:
        _cookies = cookies.split("; ")
        cookies = {}
        for cookie in _cookies:
            _cookie = cookie.split("=")
            cookies[_cookie[0]] = _cookie[1]
    else:
        exit(f"Hotbit API | Type: {type(cookies)} is currently unsupported for cookies, if you'd like to see it added please open an issue on Github")

    return cookies

def api(api_key, api_secret):
    return [api_key, api_secret]