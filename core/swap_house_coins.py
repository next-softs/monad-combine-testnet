from models.chains import Chains
from contracts.dex.MintHouse import MintHouse
from utils.logs import logger
from config import *

import random, time


def swap_house_coins(acc, wait_delay_start=True):
    client = MintHouse(acc)

    coins = SwapHouseSettings.coins.copy()
    random.shuffle(coins)

    swapped = False
    for coin in coins:
        amount = round(random.uniform(*SwapHouseSettings.amounts), random.randint(*GeneralSettings.precision))
        if client.swap_coin(coin, amount):
            swapped = True
            client.sleep(SwapHouseSettings.delay)

    if swapped and wait_delay_start:
        client.sleep(GeneralSettings.delay_start)

