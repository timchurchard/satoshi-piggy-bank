# (C) 2020 Tim Churchard

import requests

from .const import SUPPORTED_COINS, SUPPORTED_FIATS, COIN_NAMES, FIAT_SYMBOLS


class Fiat:

    def __init__(self, coin, currency='gbp'):
        if coin in SUPPORTED_COINS:
            self.__coin = coin
        else:
            raise ValueError('Unsupported coin {}'.format(coin))

        if currency in SUPPORTED_FIATS:
            self.__currency = currency
            self.__symbol = FIAT_SYMBOLS[currency]
        else:
            raise ValueError('Fiat currency {} not supported'.format(currency))

    def check_price(self):
        price = None
        name = COIN_NAMES[self.__coin].lower()
        URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency={currency}&ids={name}'.format(currency=self.__currency, name=name)
        try:
            resp = requests.get(URL)
            if resp.status_code == 200:
                price = float(resp.json()[0]['current_price'])
        except:
            # fixme: Not ideal just swallow all error and return price=None on any error
            pass
        return price

    @property
    def current_symbol(self):
        return self.__symbol
