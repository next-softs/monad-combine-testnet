from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
import random, json

class MintHouse(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "", account.proxy)
        self.coins = ["CHOG", "YAKI", "DAK"]
        random.shuffle(self.coins)

    def get_transaction_link(self, coin):
        resp = self.session.get(f"https://api.dial.to/v1/blink?apiUrl=https%3A%2F%2Funiswap.api.dial.to%2Fswap%3Fchain%3Dmonad-testnet%26inputCurrency%3Dnative%26outputCurrency%3D{coin}")
        for action in resp.json()["links"]["actions"]:
            if action["type"] == "transaction":
                return action["href"]

    def get_transaction(self, transacton_link, amount):
        resp = self.session.post(transacton_link.format(amount=amount), json={"account": self.address, "type": "transaction"})
        return json.loads(resp.json()["transaction"])

    def swap_coin(self, coin, amount):
        transaction_link = self.get_transaction_link(coin)
        data = self.get_transaction(transaction_link, amount)

        tx = {
            "chainId": self.chain_id,
            "data": data["data"],
            "from": self.w3.to_checksum_address(data["from"]),
            "to": self.w3.to_checksum_address(data["to"]),
            "value": data["value"],
            "nonce": self.nonce(),
        }

        return self.send_transaction(tx, f"swap {amount} MON > {coin} (MONAD)")
