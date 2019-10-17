#!/usr/bin/env python3

import requests

import sys

from cryptos import Bitcoin, Litecoin, Dash, dogecoin
from papirus import PapirusComposite
import pyqrcode


# Put your xpub here for Bitcoin, Litecoin, Dogecoin or Dash
# XPUB = "xpub6CPkcptFb3VQudKr4FytZfY1GumgV29pUjBqYyx2GPpX5qirZULBg5U7ynEFHriZU5LXvdoMGQWPMK8LBAeR35f32FQNEAZHG8mNsS3oFwJ"
XPUB = "ypub6X9tfM9t5GxhZwZWdAepwURh3X6JYfwbi8JtpCQB1eQGbjzyXpagoqZRxsjowgzqUhdVpoZwyrEMXUxZvYxYxuYNSyrvpKVZNjjR8YfB4Gd"
# XPUB = "Ltub2YvKWEvSpbSoNtSCwQULZLs9Ct7Q7yDoQ21mkUkCLtFuKAj9DfBCkRiC6mpp8hGjmAY16soeDgEdHmRa2UQRpnnLXdQk4oTfNVXGtTVtsn7"
# XPUB = "dgub8rEUCjTRge3oCcY2joYqnG7UwZsrtcxKVat1KYct3Kkhcjys5XBfhGWsZ2xkuB4qbgSDxR21puUtDyrkJqC3EuqrvNM7C48jE3i4xnfEsE3"
# XPUB = "drkpRyUaAg9YzaY3CZCWQ7biN5hxoNsRxHB72SUBh7vKQT8eezg8d8RoXpHfzaZx1jRmC9ZQizJXrDq2V5dXny3NHLk5523mJWGScGNpu4L4Fyx"

# User Settings
# - How many empty addresses to check
DEPTH = 10

# Computed Settings
COIN = Bitcoin
P2SH = False
TOTAL_BALANCE_FMT = "{:.8f}"
PRICE_FMT = "{:.2f}"

if XPUB.startswith("ypub"):
    P2SH = True

if XPUB.startswith("Ltub"):
    COIN = Litecoin

if XPUB.startswith("Mtub"):
    raise NotImplementedError("pybitcointools does not support P2SH for Litecoin.")

if XPUB.startswith("dgub"):
    COIN = dogecoin.Doge
    TOTAL_BALANCE_FMT = "{:.2f}"
    PRICE_FMT = "{:.5f}"

if XPUB.startswith("drkp"):
    COIN = Dash


def check_balance(addr):
    balance = None
    used = False
    if COIN == Bitcoin:
        URL = "https://blockchain.info/balance?active={}"
        try:
            resp = requests.get(URL.format(addr))
            if resp.status_code == 200:
                data = resp.json()
                balance = data[addr]['final_balance'] / 100000000
                used = True if data[addr]['n_tx'] > 0 else False
        except:
            # fixme: Not ideal just swallow all errors and return balance=None on any error
            pass
    elif COIN == Litecoin or COIN == dogecoin.Doge:
        BALANCE_URL = "http://explorer.litecoin.net/chain/Litecoin/q/addressbalance/{}"
        RECEIVED_URL = "http://explorer.litecoin.net/chain/Litecoin/q/getreceivedbyaddress/{}"
        if COIN == dogecoin.Doge:
            BALANCE_URL = "https://dogechain.info/chain/Dogecoin/q/addressbalance/{}"
            RECEIVED_URL = "http://dogechain.info/chain/Dogecoin/q/getreceivedbyaddress/{}"
        try:
            resp = requests.get(BALANCE_URL.format(addr))
            if resp.status_code == 200:
                balance = float(resp.text)
            resp = requests.get(RECEIVED_URL.format(addr))
            if resp.status_code == 200:
                used = True if float(resp.text) > 0 else False
        except:
            # fixme
            pass
    elif COIN == Dash:
        URL = "https://insight.dash.org/insight-api/addr/{}/?noTxList=1"
        try:
            resp = requests.get(URL.format(addr))
            if resp.status_code == 200:
                data = resp.json()
                balance = float(data["balance"])
                used = True if data["totalReceivedSat"] > 0 else False
        except:
            # fixme
            pass
    else:
        raise NotImplementedError("check_balance TODO")
    return balance, used


def check_fiat_price_usd():
    price = None
    coin = COIN()
    name = coin.display_name.lower()
    URL = 'https://api.coinmarketcap.com/v1/ticker/{}'.format(name)
    try:
        resp = requests.get(URL)
        if resp.status_code == 200:
            price = float(resp.json()[0]['price_usd'])
    except:
        # fixme: Not ideal just swallow all error and return price=None on any error
        pass
    return price


def generate_addr(n=0):
    coin = COIN()
    if P2SH:
        wallet = coin.watch_p2wpkh_p2sh_wallet(XPUB)
    else:
        wallet = coin.watch_wallet(XPUB)
    if not wallet.is_watching_only:
        raise ValueError("Wallet is not watch only!  Please use xpub for safety.")
    addr = wallet.receiving_address(n)
    return addr


def main():
    # Calculate total balance and find last unused address
    total_balance = 0.0
    n = 0
    remaining = DEPTH
    first_unused_addr = None
    while True:
        addr = generate_addr(n)
        balance, used = check_balance(addr)
        total_balance += balance
        print("Found n={} {} with balance {:.8f}".format(n, addr, balance))
        if not used:
            if first_unused_addr is None:
                first_unused_addr = addr
                print(" ^ First unused address")
            remaining = remaining - 1
        else:
            remaining = DEPTH
        n = n + 1
        if remaining == 0:
            break

    # Lookup fiat value of bitcoin
    price = check_fiat_price_usd()
    value = price * total_balance

    # Prepare output
    price = PRICE_FMT.format(price)
    value = PRICE_FMT.format(value)
    total_balance = TOTAL_BALANCE_FMT.format(total_balance)

    qr = pyqrcode.create(first_unused_addr)
    qr.png('/tmp/addr.png', scale=5)

    # Render to screen
    # Note: The screen I have is 2" 200x96 px.  Lots of hardcoded numbers follow.
    coin = COIN()
    comp = PapirusComposite(False)
    comp.AddImg("/tmp/addr.png", -10, -10, (96, 96), Id="Addr")

    comp.AddText("{} {}".format(total_balance, coin.coin_symbol), 10, 77, Id="total")

    comp.AddText("{}".format(coin.display_name), 90, 10, Id="title")
    comp.AddText("${}".format(value), 90, 30, Id="value")
    comp.AddText("${}".format(price), 90, 50, Id="price")

    comp.WriteAll()

    # Print infos
    print("Fiat price USD: ", price)
    print("Fiat value USD: ", value)
    print("total_balance: ", total_balance, coin.coin_symbol)


if __name__ == '__main__':
    sys.exit(main())
