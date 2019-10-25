
import requests

from .const import SUPPORTED_COINS, COIN_NAMES


class Fiat:

    def __init__(self, coin):
        if coin in SUPPORTED_COINS:
            self.__coin = coin
        else:
            raise ValueError("Fiat unsupported coin {}".format(coin))

    def check_price_usd(self):
        price = None
        name = COIN_NAMES[self.__coin].lower()
        URL = 'https://api.coinmarketcap.com/v1/ticker/{}'.format(name)
        try:
            resp = requests.get(URL)
            if resp.status_code == 200:
                price = float(resp.json()[0]['price_usd'])
        except:
            # fixme: Not ideal just swallow all error and return price=None on any error
            pass
        return price
