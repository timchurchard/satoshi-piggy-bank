
import requests

from cryptos import Bitcoin, Litecoin, Dash, dogecoin

from .const import BTC, LTC, DOGE, DASH


class Coin:  # pylint: disable=too-many-instance-attributes

    def __init__(self, xpub=None, single=None):
        self._coin = Bitcoin
        self.__balance_fmt = '{:.8f}'
        self.__price_fmt = '{:.2f}'

        self.__p2sh = False
        self.__xpub = xpub

        self.__single = single
        if self.__single is not None:
            # single address mode
            if self.__single[0] in ['1', '3', 'b']:
                # Bitcoin
                pass
            elif self.__single[0] in ['L', 'M']:
                # Litecoin
                self._coin = Litecoin
            elif self.__single[0] == 'D':
                # Dogecoin
                self._coin = dogecoin.Doge
                self.__balance_fmt = '{:.2f}'
                self.__price_fmt = '{:.4f}'
            elif self.__single[0] == 'X':
                self._coin = Dash
        else:
            # xpub mode
            if xpub.startswith('ypub'):
                self.__p2sh = True

            if xpub.startswith('Ltub'):
                self._coin = Litecoin

            if xpub.startswith('Mtub'):
                raise NotImplementedError('pybitcointools does not support P2SH for Litecoin.')

            if xpub.startswith('dgub'):
                self._coin = dogecoin.Doge
                self.__balance_fmt = '{:.2f}'
                self.__price_fmt = '{:.4f}'

            if xpub.startswith('drkp'):
                self._coin = Dash

        self.__coin_inst = self._coin()
        self.__coin = self.__coin_inst.coin_symbol

    @property
    def coin_symbol(self):
        return self.__coin_inst.coin_symbol

    @property
    def price_fmt(self):
        return self.__price_fmt

    @property
    def balance_fmt(self):
        return self.__balance_fmt

    def generate_addr(self, num=0):
        """Generate an address or return single address"""
        if self.__single is not None:
            return self.__single
        if self.__p2sh:
            wallet = self.__coin_inst.watch_p2wpkh_p2sh_wallet(self.__xpub)
        else:
            wallet = self.__coin_inst.watch_wallet(self.__xpub)
        if not wallet.is_watching_only:
            raise ValueError('Wallet is not watch only!  Please use xpub for safety.')
        addr = wallet.receiving_address(num)
        return addr

    def check_balance(self, addr):
        BALANCE_FUNCS = {
            BTC: self.__check_balance_btc,
            LTC: self.__check_balance_ltc,
            DOGE: self.__check_balance_ltc,
            DASH: self.__check_balance_dash
        }
        return BALANCE_FUNCS[self.__coin](addr)

    @classmethod
    def __check_balance_btc(cls, addr):
        URL = 'https://blockchain.info/balance?active={}'
        balance = None
        used = False
        try:
            resp = requests.get(URL.format(addr))
            if resp.status_code == 200:
                data = resp.json()
                balance = data[addr]['final_balance'] / 100000000
                used = data[addr]['n_tx'] > 0
        except:
            # fixme: Not ideal just swallow all errors and return balance=None on any error
            pass
        return balance, used

    def __check_balance_ltc(self, addr):
        balance = None
        used = False
        if self.__coin == LTC:
            BALANCE_URL = 'http://explorer.litecoin.net/chain/Litecoin/q/addressbalance/{}'
            RECEIVED_URL = 'http://explorer.litecoin.net/chain/Litecoin/q/getreceivedbyaddress/{}'
        else:
            BALANCE_URL = 'https://dogechain.info/chain/Dogecoin/q/addressbalance/{}'
            RECEIVED_URL = 'http://dogechain.info/chain/Dogecoin/q/getreceivedbyaddress/{}'
        try:
            resp = requests.get(BALANCE_URL.format(addr))
            if resp.status_code == 200:
                balance = float(resp.text)
            resp = requests.get(RECEIVED_URL.format(addr))
            if resp.status_code == 200:
                used = float(resp.text) > 0
        except:
            # fixme
            pass
        return balance, used

    @classmethod
    def __check_balance_dash(cls, addr):
        URL = 'https://insight.dash.org/insight-api/addr/{}/?noTxList=1'
        balance = None
        used = False
        try:
            resp = requests.get(URL.format(addr))
            if resp.status_code == 200:
                data = resp.json()
                balance = float(data['balance'])
                used = data['totalReceivedSat'] > 0
        except:
            # fixme
            pass
        return balance, used
