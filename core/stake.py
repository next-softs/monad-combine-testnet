from contracts.stake.Shmonad import Shmonad
from contracts.stake.Apriori import Apriori
from contracts.stake.Kintsu import Kintsu
from contracts.stake.Magma import Magma
from utils.logs import logger
from config import *

import random, time


def stake(acc, repeat_count=1, wait_delay_start=True):
    clients = {"apriori": Apriori, "kintsu": Kintsu, "magma": Magma, "shmonad": Shmonad}

    clients_list = StakeSettings.protocols.copy()
    resp = False

    for i in range(repeat_count):
        random.shuffle(clients_list)
        client = clients[clients_list[0]](acc)

        r = False

        balance_stake = float(client.token_balance(client.stake_token))
        if balance_stake > 0 and random.randint(0, 100) <= StakeSettings.withdraw:
            logger.info(f"{client.acc_name} выводим все MON из стейкинга..")
            r = client.unstake()
        else:
            amount = round(random.uniform(*StakeSettings.amounts) - balance_stake, random.randint(*GeneralSettings.precision))

            if amount > 0:
                logger.info(f"{client.acc_name} стейкаем {amount} MON..")
                r = client.stake(amount)
            elif amount < 0:
                logger.info(f"{client.acc_name} выводим {amount} MON..")
                r = client.unstake(abs(amount))

        if r:
            resp = True
            client.sleep(StakeSettings.delay)

    if resp and wait_delay_start:
        client.sleep(GeneralSettings.delay_start)