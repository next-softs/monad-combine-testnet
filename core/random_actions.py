from utils.logs import logger
from config import *

from concurrent.futures import ThreadPoolExecutor
import random, time

from .swap import swap
from .stake import stake
from .deploy import deploy
from .swap_house_coins import swap_house_coins


def start_actions(acc):
    repeat_count = random.randint(*RandomSettings.repeat_count)

    for i in range(repeat_count):
        action = random.choices(list(RandomSettings.actions.keys()), weights=list(RandomSettings.actions.values()))[0]

        if action == "swap":
            swap(acc=acc, repeat_count=random.randint(*SwapsSettings.repeat_count))

        elif action == "stake":
            stake(acc=acc, repeat_count=random.randint(*SwapsSettings.repeat_count), wait_delay_start=False)

        elif action == "deploy":
            deploy(acc=acc, wait_delay_start=False)

        elif action == "swap_house":
            swap_house_coins(acc=acc, wait_delay_start=False)
        else:
            logger.error(f"{action} действие не найдено")
            return

        timeout = random.randint(*RandomSettings.delay_actions)
        logger.info(f"ожидаем {timeout} сек. перед стартом следующего действия")
        time.sleep(timeout)


def random_actions(accounts):
    random.shuffle(accounts)

    accs = []
    for i, acc in enumerate(accounts):
        accs.append({
            "acc": acc,
            "start_time": int(time.time() + (random.randint(*GeneralSettings.delay_start) * int(i/GeneralSettings.start_accs)))
        })

    with ThreadPoolExecutor(max_workers=GeneralSettings.threads) as executor:
        while True:
            try:
                for acc in accs:
                    if time.time() >= acc["start_time"]:
                        acc["start_time"] = int(time.time() + random.randint(*RandomSettings.delay_sessions))
                        executor.submit(start_actions, acc["acc"])

            except Exception as err:
                logger.error(err)

            time.sleep(1)
