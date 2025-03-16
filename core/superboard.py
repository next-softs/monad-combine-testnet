from contracts.quests.Superboard import Superboard
from config import *

from utils.logs import logger
import random, time


def execute_quests(acc):
    try:
        client = Superboard(acc)

        client.login()
        quests = client.get_quests()
        random.shuffle(quests)

        completed = False
        for quest in quests:
            if client.execute_quest(quest):
                completed = True
                client.sleep(SuperboardSettings.delay_quest)
            else:
                time.sleep(1)

        if completed:
            client.sleep(GeneralSettings.delay_start)
    except Exception as err:
        logger.error(err)
