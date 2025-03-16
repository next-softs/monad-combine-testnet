import time

from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
from decimal import Decimal


class Orbiter(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Sepolia.rpc, [], "0xB5AADef97d81A77664fcc3f16Bfe328ad6CEc7ac", account.proxy)

    def bridge(self, amount):
        tx = {
            "chainId": self.chain_id,
            "data": "0x",
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": hex(self.gwei_to_wei(Decimal(str(amount)) + Decimal("0.001000000000009596"))),

        }

        return self.send_transaction(tx, f"bridge sepolia ETH > monad ETH ({amount} ETH)")
