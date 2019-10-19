
import pyqrcode

try:
    import papirus
    from papirus import PapirusComposite
except ImportError:
    print("WARN: Failed to import papirus.  Will fake it.")
    papirus = None

from .const import SUPPORTED_COINS, COIN_NAMES


class Draw:
    # Render to screen
    # Note: The screen I have is 2" 200x96 px.  Lots of hardcoded numbers follow.

    def __init__(self, coin):
        if coin in SUPPORTED_COINS:
            self.__coin = coin
        else:
            raise ValueError("Fiat unsupported coin {}".format(coin))

    def draw_home_screen(self, first_unused_addr, total_balance=None, price=None, value=None):
        if papirus is None:
            print("Fake: ", self.__coin, first_unused_addr, total_balance, price, value)
            return

        qr = pyqrcode.create(first_unused_addr)
        qr.png('/tmp/addr.png', scale=5)

        comp = PapirusComposite(False)
        comp.AddImg("/tmp/addr.png", -10, -10, (96, 96), Id="Addr")

        if total_balance is None:
            comp.AddText("Offline", 10, 77, Id="total")
        else:
            comp.AddText("{} {}".format(total_balance, self.__coin), 10, 77, Id="total")

        comp.AddText("{}".format(COIN_NAMES[self.__coin]), 90, 10, Id="title")

        if price is not None:
            comp.AddText("${}".format(value), 90, 30, Id="value")
            comp.AddText("${}".format(price), 90, 50, Id="price")

        comp.WriteAll()
