from contracts.dex.BeanExchange import BeanExchange
from contracts.dex.Uniswap import Uniswap

from contracts.dex.Monorail import Monorail
from contracts.dex.OctoExchange import OctoExchange


class Dex:
    def __init__(self, dex, client, coins):
        self.dex = dex
        self.client = client
        self.coins = coins

    def __repr__(self):
        return self.dex

    def check_pair(self, coin1, coin2):
        return coin1 in self.coins and coin2 in self.coins



class DexClients:
    Uniswap = Dex(dex="Uniswap", client=Uniswap, coins=["MON", "USDC", "USDT", "ETH", "WETH", "WBTC", "DAK", "MUK", "CHOG", "YAKI"])
    BeanExchange = Dex(dex="BeanExchange", client=BeanExchange, coins=["MON", "USDC"])

    Monorail = Dex(dex="Monorail", client=Monorail, coins=["MON", "USDC", "DAK", "CHOG", "YAKI"])
    OctoExchange = Dex(dex="OctoExchange", client=OctoExchange, coins=["MON", "USDC", "DAK", "CHOG", "YAKI"])
