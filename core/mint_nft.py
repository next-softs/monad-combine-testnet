from contracts.nft.MagicedenNFT import MagicedenNFT
from contracts.nft.MorkieNFT import MorkieNFT
from utils.logs import logger
from config import *

import random, time


def mint_nft_morkie(acc):
    client = MorkieNFT(acc)

    nfts = client.get_nfts()
    random.shuffle(nfts)

    resp = False
    for nft in nfts:
        balance = client.gwei_to_wei(client.token_balance(nft["address"]))
        if (balance == 0 or not MintNftSettings.mint_different):
            if MintNftSettings.max_amount < nft['amount']:
                logger.warning(f"{client.acc_name} nft стоит больше заданной цены ({nft['nft']} {nft['amount']} MON)")
                continue

            balance_mon = client.balance()
            if balance_mon <= nft["amount"]:
                logger.warning(f"{client.acc_name} недостаточно средст для минта {nft['nft']} {nft['amount']} MON")
                continue

            resp = client.mint(nft)
            if resp:
                client.sleep(MintNftSettings.delay)
        else:
            logger.warning(f"{client.acc_name} на балансе уже есть {nft['nft']} {nft['amount']} MON")
            continue

    if resp:
        client.sleep(GeneralSettings.delay_start)

def mint_nft_magiceden(acc):
    client = MagicedenNFT(acc)

    nfts = MintNftSettings.address_magiceden_nft.copy()
    random.shuffle(nfts)

    minted = False
    for nft in nfts:
        if MintNftSettings.max_amount < nft[1]:
            logger.warning(f"{client.acc_name} nft стоит больше заданной цены ({nft[0]} {nft[1]} MON)")
            continue

        nft = {"address": client.w3.to_checksum_address(nft[0]), "amount": nft[1]}

        balance = client.gwei_to_wei(client.token_balance(nft["address"]))
        if (balance == 0 or not MintNftSettings.mint_different):
            resp = client.mint(nft)
            if resp:
                minted = True
                client.sleep(MintNftSettings.delay)
        else:
            logger.warning(f"{client.acc_name} на балансе уже есть {nft['address']} {nft['amount']} MON")
            continue

    if minted:
        client.sleep(GeneralSettings.delay_start)