from contracts.deploy.Owlto import Owlto
from config import *

from utils.logs import logger
import random, time


def deploy(acc, wait_delay_start=True):
    client = Owlto(acc)

    resp = client.deploy()
    if resp and wait_delay_start:
        client.sleep(GeneralSettings.delay_start)

    return resp