import time

from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
from decimal import Decimal


class Shmonad(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "0x3a98250F98Dd388C211206983453837C8365BDc1", account.proxy)
        self.stake_token = "0x3a98250F98Dd388C211206983453837C8365BDc1"

    def stake(self, amount):
        amount_wei_hex = hex(self.gwei_to_wei(amount))
        data = get_data_byte64("0x6e553f65", amount_wei_hex, self.address)

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": amount_wei_hex
        }

        return self.send_transaction(tx, f"stake {amount} MON (shMonad)")


    def unstake(self, amount=0):
        if amount == 0:
            amount = self.token_balance(self.stake_token)

        amount_wei_hex = hex(self.gwei_to_wei(amount))
        data = get_data_byte64("0xba087652", amount_wei_hex, self.address, self.address)

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address
        }

        return self.send_transaction(tx, f"unstake {amount} MON (shMonad)")

