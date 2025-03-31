import datetime

from contracts.bridge.GasZip import GasZip
from models.chains import Chains
from utils.logs import logger
from config import *

import random, time


def faucet_gas_zip(accounts):
    accs_info = []

    for acc in accounts:
        accs_info.append({
            "acc": acc,
            "client": GasZip(acc, Chains.Monad),
            "claim_time": 0
        })

    random.shuffle(accs_info)

    def next_claim(info_wallet):
        if "next_claim_time" in info_wallet and info_wallet["next_claim_time"] > 0:
            claim_time = info_wallet["next_claim_time"]
        else:
            if info_wallet["last_claim_time"] > 0:
                claim_time = info_wallet["last_claim_time"] + 3600 * 12 + 1

            else:
                claim_time = int(time.time() + 3600 * 12 + 1)

        claim_time += random.randint(*RandomSettings.delay_faucets)
        logger.info(f"{client.acc_name} следующий клейм {datetime.datetime.fromtimestamp(claim_time)}")
        return claim_time

    while True:
        try:
            for acc_info in accs_info.copy():
                client = acc_info["client"]
                if time.time() > acc_info["claim_time"]:
                    info_wallet = client.get_info_wallet()

                    if info_wallet["last_claim_time"] == 0 and info_wallet["num_deposits"] >= 10:
                        client.claim()
                        time.sleep(3)

                        info_wallet = client.get_info_wallet()
                        if info_wallet["eligibility"] == "CLAIMED":
                            logger.success(f"{client.acc_name} получили {info_wallet['reward_amount']} MON")
                            acc_info["claim_time"] = next_claim(info_wallet)
                            continue

                    elif info_wallet["num_deposits"] >= 10 and info_wallet["last_claim_time"] >= 0:
                        acc_info["claim_time"] = next_claim(info_wallet)
                        continue

                    elif info_wallet["num_deposits"] < 10:
                        logger.warning(f"{client.acc_name} на кошельке меньше 10 транзакций gas.zip")
                        acc_info["claim_time"] = next_claim(info_wallet)

        except Exception as err:
            logger.error(err)

        time.sleep(60)