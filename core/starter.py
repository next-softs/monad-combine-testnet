from concurrent.futures import ThreadPoolExecutor
from config import GeneralSettings
from random import shuffle

def start_func(func, accounts, **kwargs):
    results = []

    accounts = accounts.copy()
    shuffle(accounts)

    with ThreadPoolExecutor(max_workers=GeneralSettings.threads) as executor:
        futures = [executor.submit(func, acc, **kwargs) for acc in accounts]
        results = [future.result() for future in futures]

    return results