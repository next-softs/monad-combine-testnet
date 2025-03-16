from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains


class GasZip(Default):
    def __init__(self, account, chain):
        super().__init__(account.private_key, chain.rpc, [], "", account.proxy)
        self.chain = chain

    def bridge(self, amount):
        tx = {
            "chainId": self.chain_id,
            "data": "0x0101b1",
            "from": self.address,
            "nonce": self.nonce(),
            "to": "0x391E7C679d29bD940d63be94AD22A25d25b5A604",
            "value": hex(self.gwei_to_wei(amount*1.05))
        }

        return self.send_transaction(tx, f"bridge gas.zip {self.chain.chain} ETH > monad ETH ({amount} ETH)")
