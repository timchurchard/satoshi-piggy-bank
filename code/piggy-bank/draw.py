# pylint: disable=C0121
# C0121 singleton-comparison for GPIO == False because is False does not work

import os.path
from os import system
from time import sleep

import pyqrcode

try:
    from papirus import PapirusComposite
    papirus = True
except ImportError:
    print('WARN: Failed to import papirus.  Will fake it.')
    papirus = None

try:
    import RPi.GPIO as GPIO
except ImportError:
    pass

from .const import SUPPORTED_COINS, COIN_NAMES
from .util import get_total_balance, format_total_price


# Assume Papirus Zero
SW1 = 21
SW2 = 16
SW3 = 20
SW4 = 19
SW5 = 26  # Set to -1 if not using RPI Zero

# Graphics paths
GFX_PATH = os.path.join(os.path.split(__file__)[0], 'gfx')
MENU_ICON = os.path.join(GFX_PATH, 'menu.png')
MENU_TOP = os.path.join(GFX_PATH, 'top.png')
MENU_OFF = os.path.join(GFX_PATH, 'shutdown.png')


class Draw:
    # Render to screen
    # Note: The screen I have is 2' 200x96 px.  Lots of hardcoded numbers follow.

    def __init__(self, coin, gui=False):
        if coin in SUPPORTED_COINS:
            self.__coin = coin
        else:
            raise ValueError('Fiat unsupported coin {}'.format(coin))

        self.__gui = gui

    def draw_home_screen(self, first_unused_addr, total_balance=None, price=None, value=None, gfx=None):
        if papirus is None:
            print('Fake: ', self.__coin, first_unused_addr, total_balance, price, value)
            return

        qr = pyqrcode.create(first_unused_addr)
        qr.png('/tmp/addr.png', scale=5)

        comp = PapirusComposite(False)
        comp.AddImg('/tmp/addr.png', -10, -10, (96, 96), Id='addr')

        if total_balance is None:
            comp.AddText('Offline', 10, 77, Id='total')
        else:
            comp.AddText('{} {}'.format(total_balance, self.__coin), 10, 77, Id='total')

        comp.AddText('{}'.format(COIN_NAMES[self.__coin]), 90, 10, Id='title')

        if price is not None:
            comp.AddText('${}'.format(value), 90, 30, Id='value')
            comp.AddText('${}'.format(price), 90, 50, Id='price')

        if self.__gui and papirus:
            if gfx == MENU_TOP:
                comp.AddImg(MENU_TOP, 0, 0, (200, 14), Id='menu')
            else:
                # Show the menu icon top right
                comp.AddImg(MENU_ICON, 160, 0, (40, 14), Id='menu')

        comp.WriteAll()

    @classmethod
    def draw_shutdown_option(cls):
        comp = PapirusComposite(False)
        comp.AddImg(MENU_OFF, 0, 0, (200, 96), Id='off')
        comp.WriteAll()

    @classmethod
    def draw_address(cls, addr):
        comp = PapirusComposite(False)
        comp.AddText(addr, 10, 30, (180, 66), Id='addr')
        comp.WriteAll()

    @classmethod
    def __wait_for_button(cls):
        BUTTONS = [SW1, SW2, SW3, SW4, SW5]

        GPIO.setmode(GPIO.BCM)

        GPIO.setup(SW1, GPIO.IN)
        GPIO.setup(SW2, GPIO.IN)
        GPIO.setup(SW3, GPIO.IN)
        GPIO.setup(SW4, GPIO.IN)
        if SW5 != -1:
            GPIO.setup(SW5, GPIO.IN)

        try:
            while True:
                # Exit when SW1 and SW2 are pressed simultaneously
                if (GPIO.input(SW1) == False) and (GPIO.input(SW2) == False):  # noqa
                    print('Exiting... ')
                    return 0

                for b in BUTTONS:
                    if b == -1:
                        continue
                    if GPIO.input(b) == False:  # noqa  (== False not is False, todo: investigate)
                        while GPIO.input(b) == False:  # noqa
                            sleep(0.01)  # Debounce
                        return 1 + BUTTONS.index(b)

                sleep(0.1)
        except KeyboardInterrupt:
            return 0

    def gui_main_loop(self, coin, fiat, depth, first_unused_addr, total_balance, price, value):
        if papirus is None:
            return
        screen = 0
        menu_shown = False
        while True:
            print('Running GUI main loop...')
            bpress = self.__wait_for_button()
            if screen == 0:
                # Homescreen QR code and balance
                if bpress == 0:
                    break
                if bpress == 1:
                    # Show Menu
                    self.draw_home_screen(first_unused_addr, total_balance, price, value, gfx=MENU_TOP if not menu_shown else MENU_ICON)
                    menu_shown = not menu_shown
                if bpress == 5:
                    # Show Shutdown option
                    screen = 1
                    self.draw_shutdown_option()
                if bpress == 4:
                    # Show Address text
                    screen = 2
                    self.draw_address(first_unused_addr)
                if bpress == 3:
                    # Update balance
                    total_balance, first_unused_addr = get_total_balance(depth, coin)
                    price = fiat.check_price_usd()
                    total_balance, price, value = format_total_price(coin, total_balance, price)

            if screen == 1:
                # Shutdown
                if bpress >= 4:
                    self.__gui = False
                    self.draw_home_screen(first_unused_addr, total_balance, price, value, gfx=MENU_TOP if not menu_shown else MENU_ICON)
                    sleep(0.25)
                    system('sudo halt')
                else:
                    self.draw_home_screen(first_unused_addr, total_balance, price, value, gfx=MENU_TOP if not menu_shown else MENU_ICON)
                    menu_shown = False
                    screen = 0
            if screen == 2:
                # Show text address
                self.draw_home_screen(first_unused_addr, total_balance, price, value, gfx=MENU_TOP if not menu_shown else MENU_ICON)
                menu_shown = False
                screen = 0
