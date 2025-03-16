from contracts.bridge.GasZip import GasZip
from models.chains import Chains
from utils.logs import logger


def account_info(acc):
    client = GasZip(acc, Chains.Monad)
    logger.info(f"{client.acc_name} {round(client.balance(), 6)} MON | tx count: {int(client.nonce(), 16)}")