#!/usr/bin/env python3
# (C) 2019 Tim Churchard

from sys import exit as sysexit

import argparse
from random import choice as random_choice

from .fiat import Fiat
from .coin import Coin
from .draw import Draw
from .const import DEFAULT_DEPTH, EXAMPLE_XPUBS
from .util import get_total_balance, format_total_price


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", help="how many addresses to check after the first unused address", default=DEFAULT_DEPTH)
    parser.add_argument("--xpub", help="xpub of watch only wallet in Bitcoin, Litecoin, Dogecoin or Dash")
    parser.add_argument("--single", help="single address to watch")
    parser.add_argument("--gui", help="Continue running in GUI mode (papirus only)", action="store_true")
    args = parser.parse_args()

    xpub = None
    if args.xpub is None and args.single is None:
        print("WARN: --xpub or --single not specified.  Will use example xpub!")
        xpub = random_choice(EXAMPLE_XPUBS)
    if args.xpub is not None:
        xpub = args.xpub

    coin = Coin(xpub=xpub, single=args.single)
    fiat = Fiat(coin.coin_symbol)
    draw = Draw(coin.coin_symbol, gui=args.gui)

    total_balance, first_unused_addr = get_total_balance(args.depth, coin)

    # Lookup fiat value of bitcoin
    price = fiat.check_price_usd()

    if price is None:
        draw.draw_home_screen(first_unused_addr)

    else:
        total_balance, price, value = format_total_price(coin, total_balance, price)

        draw.draw_home_screen(first_unused_addr, total_balance, price, value)

        # Print infos
        print("Fiat price USD: ", price)
        print("Fiat value USD: ", value)
        print("total_balance: ", total_balance)

    # Run the GUI loop until user hits shutdown!
    if args.gui:
        draw.gui_main_loop(coin, fiat, args.depth, first_unused_addr, total_balance, price, value)


if __name__ == '__main__':
    sysexit(main())
