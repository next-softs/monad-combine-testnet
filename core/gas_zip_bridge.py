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

    chains = {"op": Chains.OP, "arb": Chains.ARB, "base": Chains.Base, "unichan": Chains.Unichain}
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

def spam_transactions(acc):
    client = GasZip(acc, Chains.Monad)
    wallet_info = client.get_info_wallet()

    if wallet_info["num_deposits"] < GasZipSettings.count_transactions:
        count_transactions = round(GasZipSettings.count_transactions - wallet_info["num_deposits"])
        logger.info(f"{client.acc_name} будет сделано {count_transactions} транзакций")

        chains = {"op": Chains.OP, "arb": Chains.ARB, "base": Chains.Base, "unichan": Chains.Unichain}
        chains_list = []

        for c in chains.keys():
            if c in GasZipSettings.chains_transactions:
                chains_list.append(c)

        bridged = False
        for i in range(count_transactions):
            random.shuffle(chains_list)

            for i in range(3):
                for chain in chains_list:
                    client = GasZip(acc, chains[chain])
                    balance = client.balance()
                    if balance > GasZipSettings.amounts_transactions[1]:
                        amount = round(random.uniform(*GasZipSettings.amounts_transactions), random.randint(*GeneralSettings.precision))

                        if GasZipSettings.use_same_chain:
                            chain_out = chains[chains_list[0]]
                        else:
                            chain_out = chains_list.copy()
                            chain_out.remove(chain)

                            chain_out = chains[chain_out[0]]

                        resp = client.bridge_for_transaction(chain_out=chain_out, amount=amount)

                        if resp:
                            bridged = True
                            client.sleep(GasZipSettings.delay_transactions)
                            break
                else:
                    if bridged:
                        logger.info(f"{client.acc_name} ождиаем пополнение 3 мин.")
                        time.sleep(180)
                        continue
                    else:
                        logger.warning(f"{client.acc_name} на балансе нет нужного кол-ва ETH {client.address}")
                        return

                break

    else:
        logger.warning(f"{client.acc_name} на кошельке уже есть {wallet_info['num_deposits']} транзакций")

