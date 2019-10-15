#!/usr/bin/env python3

import requests

import sys

from cryptos import Bitcoin
from papirus import PapirusComposite
import pyqrcode


DEFAULT_COIN = Bitcoin
XPUB = "xpub6CPkcptFb3VQudKr4FytZfY1GumgV29pUjBqYyx2GPpX5qirZULBg5U7ynEFHriZU5LXvdoMGQWPMK8LBAeR35f32FQNEAZHG8mNsS3oFwJ"


def check_balance(addr):
    # Note: Extend this for other coins?
    balance = None
    if DEFAULT_COIN == Bitcoin:
        URL = "https://blockchain.info/es/q/addressbalance/{}"
        try:
            resp = requests.get(URL.format(addr))
            if resp.status_code == 200:
                balance = float(int(resp.text) / 100000000)
        except:
            # fixme: Not ideal just swallow all errors and return balance=None on any error
            pass
    else:
        raise NotImplementedError("check_balance not Bitcoin TODO")
    return balance


def check_fiat_price_usd():
    price = None
    if DEFAULT_COIN == Bitcoin:
        URL = 'https://api.coinmarketcap.com/v1/ticker/bitcoin'
        try:
            resp = requests.get(URL)
            if resp.status_code == 200:
                price = float(resp.json()[0]['price_usd'])
        except:
            # fixme: Not ideal just swallow all error and return price=None on any error
            pass
    else:
        raise NotImplementedError("check_balance not Bitcoin TODO")
    return price


def generate_addr(n=0):
    coin = DEFAULT_COIN()
    wallet = coin.watch_wallet(XPUB)
    if not wallet.is_watching_only:
        raise ValueError("Wallet is not watch only!  Please use xpub for safety.")
    addr = wallet.receiving_address(n)
    return addr


def main():
    # Calculate total balance and find last unused address
    total_balance = 0.0
    n = 0
    while True:
        addr = generate_addr(n)
        balance = check_balance(addr)
        total_balance += balance
        print("Found {} with balance {:.8f}".format(addr, balance))
        if balance == 0:
            break
        n = n + 1

    # Lookup fiat value of bitcoin
    price = check_fiat_price_usd()
    value = price * total_balance

    # Prepare output
    price = "{:.2f}".format(price)
    value = "{:.2f}".format(value)
    total_balance = "{:.8f}".format(total_balance)

    qr = pyqrcode.create(addr)
    qr.png('/tmp/addr.png', scale=5)

    # Render to screen
    # Note: The screen I have is 2" 200x96 px.  Lots of hardcoded numbers follow.
    comp = PapirusComposite(False)
    comp.AddImg("/tmp/addr.png", -10, -10, (96, 96), Id="Addr")

    comp.AddText("{} BTC".format(total_balance), 10, 77, Id="total")

    comp.AddText("Bitcoin", 90, 10, Id="title")
    comp.AddText("${}".format(value), 90, 30, Id="value")
    comp.AddText("${}".format(price), 90, 50, Id="price")

    comp.WriteAll()

    # Print infos
    print("Fiat price USD: ", price)
    print("Fiat value USD: ", value)
    print("total_balance BTC", total_balance)


if __name__ == '__main__':
    sys.exit(main())
