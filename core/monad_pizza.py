from contracts.quests.MonadPizza import MonadPizza

from utils.logs import logger
from config import *

from concurrent.futures import ThreadPoolExecutor
import random, time


def monad_pizza(acc):
    try:
        if acc["client"] is None:
            acc["client"] = MonadPizza(acc["acc"])

        client = acc["client"]
        time_now = int(time.time())

        if time_now >= acc["start_time"]:
            if acc["check_reg"]:
                client.register()

                acc["battle_pass"] = client.check_battle_pass()
                acc["click_time"] = client.can_click()
                acc["auto_click_time"] = client.get_time_active_boost()
                acc["check_reg"] = False
        else:
            return

        # делаем клики
        if time_now > acc["click_time"] and time_now > acc["auto_click_time"] and acc["start_click"]:
            acc["start_click"] = False
            for i in range(random.randint(*MonadPizzaSettings.clicks)):
                acc["click_time"] = client.click()
                click_cooldown = client.click_cooldown()

                client.sleep([MonadPizzaSettings.delay_clicks[0] + click_cooldown, MonadPizzaSettings.delay_clicks[1] + click_cooldown])

        # покупаем пропуски
        if MonadPizzaSettings.buy_battle_pass and acc["battle_pass"] < 3:
            for i in range(round(3 - acc["battle_pass"])):
                client.buy_battle_pass()
                acc["battle_pass"] += 1
                client.sleep(MonadPizzaSettings.delay_battle_pass)

        # клеймим бейджи
        if MonadPizzaSettings.badges_claim:
            badges_info = client.get_info_badges()
            for badge in badges_info:
                if badge["isAvailable"] and not badge["isMint"]:
                    client.claim_badge(badge["tokenId"], badge["price"], badge["name"])
                    client.sleep(MonadPizzaSettings.delay_badges)

        # запускаем автокликер
        if time_now > acc["click_time"] and time_now > acc["auto_click_time"]:
            client.click()
            time.sleep(5)

            acc["auto_click_time"] = client.start_auto_clicker()
            acc["start_click"] = True

        acc["start_time"] = int(time.time() + 10)

    except Exception as err:
        logger.error(err)

def start_monad_pizza(accounts):
    random.shuffle(accounts)

    accs = {}
    for i, acc in enumerate(accounts):
        acc_name = acc.name
        if acc_name not in accs:
            accs[acc_name] = {
                "start_time": int(time.time() + (random.randint(*GeneralSettings.delay_start) * int(i / GeneralSettings.start_accs))),
                "acc": acc,
                "client": None,
                "check_reg": True,
                "start_click": True,
                "click_time": 0,
                "auto_click_time": 0,
                "battle_pass": 0
            }

    while True:
        try:
            with ThreadPoolExecutor(max_workers=GeneralSettings.threads) as executor:
                for acc in accs.values():
                    if time.time() >= acc["start_time"]:
                        executor.submit(monad_pizza, acc)


        except Exception as err:
            logger.error(err)

        time.sleep(1)