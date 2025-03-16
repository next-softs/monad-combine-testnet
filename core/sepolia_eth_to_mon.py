from contracts.dex.Ambient import Ambient
from contracts.bridge.Orbiter import Orbiter
from models.coins import Coins

from utils.logs import logger
from config import *

import random, time


def sepolia_eth_to_mon(acc):
    client_orbiter = Orbiter(acc)
    client_ambient = Ambient(acc)

    balance_mon = client_ambient.balance()
    if  balance_mon == 0:
        logger.warning(f"{client_ambient.acc_name} кошельке нет MON для оплаты комиссии за свап ETH > MON")
        return

    if balance_mon >= SepoliaToMonSettings.max_amount:
        logger.warning(f"{client_ambient.acc_name} на балансе уже есть {balance_mon}, переводить ничего не будем")
        return

    amount = round(random.uniform(*SepoliaToMonSettings.amounts), random.randint(*GeneralSettings.precision))
    balance_eth = float(client_ambient.token_balance(Coins.ETH.address))

    if amount > balance_eth or not SepoliaToMonSettings.use_eth_monad:
        amount_bridge = amount
        if SepoliaToMonSettings.use_eth_monad:
            amount_bridge = round(amount - balance_eth, random.randint(*GeneralSettings.precision))
            logger.info(f"{client_ambient.acc_name} бриджить будем {amount_bridge} ETH | на балансе monad {balance_eth} ETH ")

        client_orbiter.bridge(amount_bridge)
    else:
        logger.info(f"{client_ambient.acc_name} уже есть необходимое кол-во ETH в MONAD, бриджить не будем")

    for i in range(30):
        balance_eth = float(client_ambient.token_balance(Coins.ETH.address))
        if balance_eth >= amount - 0.0065:
            logger.info(f"{client_ambient.acc_name} ETH поступили в MONAD {balance_eth}")
            break
        client_ambient.sleep([60, 60])

    else:
        logger.warning(f"{client_ambient.acc_name} ETH так и не поступили в MONAD {balance_eth}")
        return

    amount = round(amount - random.uniform(0.007, 0.0088), random.randint(*GeneralSettings.precision))
    resp = client_ambient.swap(amount)

    if resp:
        client_orbiter.sleep(GeneralSettings.delay_start)

    return resp

