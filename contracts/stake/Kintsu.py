import time

from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
from decimal import Decimal


class Kintsu(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "0x07AabD925866E8353407E67C1D157836f7Ad923e", account.proxy)
        self.stake_token = "0x07AabD925866E8353407E67C1D157836f7Ad923e"

    def stake(self, amount):
        amount_wei_hex = hex(self.gwei_to_wei(amount))

        tx = {
            "chainId": self.chain_id,
            "data": "0x3a4b66f1",
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": amount_wei_hex
        }

        return self.send_transaction(tx, f"stake {amount} MON (Kintsu)")


    def unstake(self, amount=0):
        if amount == 0:
            amount = self.token_balance(self.stake_token)

        amount_wei_hex = hex(self.gwei_to_wei(amount))
        data = get_data_byte64("0x30af6b2e", amount_wei_hex)

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address
        }

        return self.send_transaction(tx, f"unstake {amount} MON (Kintsu)")

