from models.dex import *
from models.coins import *

from utils.logs import logger
from config import *

from concurrent.futures import ThreadPoolExecutor
import random, time


def form_balance(balance):
    return round(float(balance) - random.uniform(0.000001, 0.000005), 6)

def get_dex_list():
    dex_list = [value for key, value in vars(DexClients).items() if not key.startswith("__") and isinstance(value, Dex)]

    for dex in dex_list.copy():
        if dex.dex not in SwapsSettings.exchanges:
            dex_list.remove(dex)

    random.shuffle(dex_list)

    return dex_list

def generate_swap_params(acc, dex):
    coins_list = [value for key, value in vars(Coins).items() if not key.startswith("__") and isinstance(value, CoinInfo)]
    random.shuffle(coins_list)

    coins = {}

    for coin in coins_list:
        if coin.coin in SwapsSettings.coins and coin.coin in dex.coins:
            coins[coin.coin] = coin

    client = dex.client(acc)

    if not coins:
        logger.warning(f"{client.acc_name} нет подходящих монет")
        return

    pair = {"in_token": None, "out_token": None, "in_amount": 0}

    amount_buy = round(random.uniform(*SwapsSettings.amounts), random.randint(*GeneralSettings.precision))
    balance_mon = float(client.balance())
    if balance_mon - amount_buy <= SwapsSettings.min_balance_mon:
        logger.info(f"{client.acc_name} принудительно продаем монеты, баланс {round(balance_mon, 4)} MON")
        side = "sell"
    else:
        side = random.choice(["buy", "sell"])

    if side == "sell":
        for coin in coins.values():
            if coin.coin != "MON":
                balance = form_balance(client.token_balance(coin.address))
                if balance > 0.000005:
                    pair["in_token"] = coin
                    pair["out_token"] = coins["MON"]
                    pair["in_amount"] = balance
                    break
        else:
            side = "buy"

    if side == "buy":
        pair["in_token"] = coins["MON"]
        del coins["MON"]

        pair["out_token"] = coins[random.choice(list(coins.keys()))]
        pair["in_amount"] = amount_buy

    logger.info(f"{client.acc_name} сгенерирована пара {pair['in_amount']} {pair['in_token']} > {pair['out_token']} ({dex.dex})")
    return pair["in_token"], pair["out_token"], pair["in_amount"]

def swap(acc, in_token=None, out_token=None, in_amount=None, repeat_count=1):
    dex_list = get_dex_list()

    for dex in dex_list.copy():
        if dex.dex not in SwapsSettings.exchanges:
            dex_list.remove(dex)

    resp = False
    get_pair = False
    for i in range(repeat_count):
        resp = False
        random.shuffle(dex_list)

        for dex in dex_list:
            if get_pair or (not in_token or not out_token):
                in_token, out_token, in_amount = generate_swap_params(acc, dex)
                get_pair = True

            if dex.check_pair(in_token.coin, out_token.coin):
                client = dex.client(acc)

                resp = client.swap(
                    in_token=in_token,
                    out_token=out_token,
                    in_amount=in_amount
                )

                if resp:
                    if in_token.coin in ["MON", "WMON"]:
                        if random.randint(0, 100) <= SwapsSettings.auto_sell:
                            client.sleep(SwapsSettings.delay_swap)
                            amount = client.token_balance(out_token.address)
                            logger.info(f"{acc.name} продаем {amount} {out_token.coin} после покупки..")
                            swap(acc, out_token, in_token, amount)
                    break
        else:
            logger.warning(f"{acc.name} нет пары на дексах {in_token.coin} > {out_token.coin}")

        if resp:
            client.sleep(SwapsSettings.delay_swap)

    return resp

def random_swaps(accounts):
    accs = []
    for i, acc in enumerate(accounts):
        accs.append({
            "acc": acc,
            "start_time": int(time.time() + (random.randint(*GeneralSettings.delay_start) * int(i/GeneralSettings.start_accs)))
        })

    random.shuffle(accs)

    with ThreadPoolExecutor(max_workers=GeneralSettings.threads) as executor:
        while True:
            try:
                for acc in accs:
                    if time.time() >= acc["start_time"]:
                        acc["start_time"] = int(time.time() + random.randint(*SwapsSettings.delay_sessions))
                        executor.submit(swap, acc["acc"])

            except Exception as err:
                logger.error(err)

            time.sleep(1)

def swap_tokens_to_mon(acc):
    coins_list = [value for key, value in vars(Coins).items() if not key.startswith("__") and isinstance(value, CoinInfo)]
    random.shuffle(coins_list)

    dex_list = get_dex_list()

    swapped = False
    for coin in coins_list:
        if coin.coin in ["MON", "WMON"]: continue

        random.shuffle(dex_list)
        for dex in dex_list:
            if coin.coin in dex.coins:
                client = dex.client(acc)
                balance = form_balance(client.token_balance(coin.address))

                if balance > 0.000005:
                    logger.info(f"{client.acc_name} меняем {balance} {coin.coin} > MON ({dex.dex})")

                    if swap(acc, coin, Coins.MON, balance):
                        client.sleep(SwapsSettings.delay_swap)
                        swapped = True

    if swapped:
        client.sleep(GeneralSettings.delay_start)

