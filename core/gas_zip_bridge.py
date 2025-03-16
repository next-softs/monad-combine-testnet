from contracts.bridge.GasZip import GasZip
from models.chains import Chains
from utils.logs import logger
from config import *

import random, time


def gas_zip_bridge(acc):
    client = GasZip(acc, Chains.Monad)
    balance = client.balance()

    if balance >= GasZipSettings.max_amount:
        logger.warning(f"{client.acc_name} бриджить не будем т.к. на балансе {round(balance, 6)} MON")
        return True

    amount = round(random.uniform(*GasZipSettings.amounts), random.randint(*GeneralSettings.precision))

    chains = {"op": Chains.OP, "arb": Chains.ARB, "base": Chains.Base}
    chains_list = list(chains.keys())
    random.shuffle(chains_list)

    balances = {}

    for c in chains_list:
        if c not in GasZipSettings.chains: continue

        client = GasZip(acc, chains[c])
        balance = client.balance()
        if balance > amount: break

        balances[c] = round(balance, 6)

    else:
        logger.warning(f"{client.acc_name} недостаточно ETH, нужно {amount} | балансы: {balances}")
        return False

    resp = client.bridge(amount)

    if resp:
        client.sleep(GeneralSettings.delay_start)

    return resp

