#!/usr/bin/env python3
# (C) 2019 Tim Churchard

from sys import exit as sysexit

import argparse
from random import choice as random_choice

from .fiat import Fiat
from .coin import Coin
from .draw import Draw
from .const import DEFAULT_DEPTH, EXAMPLE_XPUBS


def get_total_balance(depth, coin):
    # Calculate total balance and find last unused address
    total_balance = 0.0
    first_unused_addr = None

    remaining = depth
    n = 0
    while True:
        addr = coin.generate_addr(n)
        balance, used = coin.check_balance(addr)
        if balance is None:
            # Note: Assume no internet so exit loop
            print("Running in offline mode. Addr {}".format(addr))
            first_unused_addr = addr
            break
        total_balance += balance
        print("Found n={} {} with balance {:.8f}".format(n, addr, balance))
        if not used:
            if first_unused_addr is None:
                first_unused_addr = addr
                print(" ^ First unused address")
            remaining = remaining - 1
        else:
            remaining = depth
        n = n + 1
        if remaining == 0:
            break

        if n == 1 and addr == coin.generate_addr(n):
            # Single mode!
            first_unused_addr = addr
            break
    return total_balance, first_unused_addr


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", help="how many addresses to check after the first unused address", default=DEFAULT_DEPTH)
    parser.add_argument("--xpub", help="xpub of watch only wallet in Bitcoin, Litecoin, Dogecoin or Dash")
    parser.add_argument("--single", help="single address to watch")
    args = parser.parse_args()

    xpub = None
    if args.xpub is None and args.single is None:
        print("WARN: --xpub or --single not specified.  Will use example xpub!")
        xpub = random_choice(EXAMPLE_XPUBS)

    coin = Coin(xpub=xpub, single=args.single)
    fiat = Fiat(coin.coin_symbol)
    draw = Draw(coin.coin_symbol)

    total_balance, first_unused_addr = get_total_balance(args.depth, coin)

    # Lookup fiat value of bitcoin
    price = fiat.check_price_usd()

    if price is None:
        draw.draw_home_screen(first_unused_addr)

    else:
        value = price * total_balance
        price = coin.price_fmt.format(price)
        value = coin.price_fmt.format(value)
        total_balance = coin.balance_fmt.format(total_balance)

        draw.draw_home_screen(first_unused_addr, total_balance, price, value)

        # Print infos
        print("Fiat price USD: ", price)
        print("Fiat value USD: ", value)
        print("total_balance: ", total_balance)


if __name__ == '__main__':
    sysexit(main())
