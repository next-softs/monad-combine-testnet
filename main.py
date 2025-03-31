import threading
import time

from models.accounts import Accounts

from utils.first_message import first_message, get_action
from utils.logs import logger
from config import *

from core.stake import stake
from core.deploy import deploy
from core.starter import start_func
from core.faucets import faucet_gas_zip
from core.mint_nft import mint_nft_morkie
from core.account_info import account_info
from core.superboard import execute_quests
from core.mint_nft import mint_nft_magiceden
from core.monad_pizza import start_monad_pizza
from core.swap_house_coins import swap_house_coins
from core.sepolia_eth_to_mon import sepolia_eth_to_mon
from core.swap import swap, random_swaps, swap_tokens_to_mon
from core.random_actions import random_actions, start_actions
from core.gas_zip_bridge import gas_zip_bridge, spam_transactions


def start_action(action):
    accounts_manager = Accounts()
    accounts_manager.loads_accs()
    accounts = accounts_manager.accounts

    if action == "Получить монеты MON":
        action = get_action(["Купить монеты gas.zip", "Обменять Sepolia ETH на MON"])

        if action == "Купить монеты gas.zip":
            start_func(gas_zip_bridge, accounts)
        elif action == "Обменять Sepolia ETH на MON":
            start_func(sepolia_eth_to_mon, accounts)

    elif action == "Минт NFT":
        action = get_action(["Morkie NFT", "Magiceden NFT"])

        if action == "Morkie NFT":
            start_func(mint_nft_morkie, accounts)
        elif action == "Magiceden NFT":
            start_func(mint_nft_magiceden, accounts)

    elif action == "Свапы":
        action = get_action(["Рандомные свапы", "Перевести все монеты в MON", "Купить House монеты (оф. сайт)"])

        if action == "Купить House монеты (оф. сайт)":
            start_func(swap_house_coins, accounts)
        elif action == "Рандомные свапы":
            random_swaps(accounts)
        elif action == "Перевести все монеты в MON":
            start_func(swap_tokens_to_mon, accounts)

    elif action == "Краны":
        action = get_action(["gas.zip"])

        if action == "gas.zip":
            action = get_action(["Накрутка транзакций", "Клейм монет"])

            if action == "Накрутка транзакций":
                start_func(spam_transactions, accounts)
            elif action == "Клейм монет":
                faucet_gas_zip(accounts)

    elif action == "Стейкинг":
        start_func(stake, accounts)

    elif action == "Баланс и кол-во транзакций":
        start_func(account_info, accounts)

    elif action == "Рандомные действия":
        if RandomSettings.monad_pizza:
            threading.Thread(target=start_monad_pizza, args=(accounts,)).start()

        random_actions(accounts)

    elif action == "Получить награды Superboard":
        start_func(execute_quests, accounts)

    elif action == "Monad.Pizza":
        start_monad_pizza(accounts.copy())


def main():
    action = get_action(["Рандомные действия", "Получить награды Superboard", "Баланс и кол-во транзакций", "Получить монеты MON", "Monad.Pizza", "Минт NFT", "Стейкинг", "Свапы", "Краны"])
    start_action(action)


if __name__ == '__main__':
    first_message()
    main()
