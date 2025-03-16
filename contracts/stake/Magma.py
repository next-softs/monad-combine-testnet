import time

from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
from decimal import Decimal


class Magma(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "0x2c9C959516e9AAEdB2C748224a41249202ca8BE7", account.proxy)
        self.stake_token = "0xaEef2f6B429Cb59C9B2D7bB2141ADa993E8571c3"

    def stake(self, amount):
        amount_wei_hex = hex(self.gwei_to_wei(amount))

        tx = {
            "chainId": self.chain_id,
            "data": "0xd5575982",
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": amount_wei_hex
        }

        return self.send_transaction(tx, f"stake {amount} MON (Magma)")


    def unstake(self, amount=0):
        if amount == 0:
            amount = self.token_balance(self.stake_token)

        amount_wei_hex = hex(self.gwei_to_wei(amount))
        data = get_data_byte64("0x6fed1ea7", amount_wei_hex)

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address
        }

        return self.send_transaction(tx, f"unstake {amount} MON (Magma)")

