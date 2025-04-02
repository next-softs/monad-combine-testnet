from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
from utils.logs import logger


class GasZip(Default):
    def __init__(self, account, chain):
        super().__init__(account.private_key, chain.rpc, [], "", account.proxy)
        self.chain = chain

    def call(self, method, url, **kwargs):
        resp = self.session.request(method, url, timeout=10, **kwargs)
        return resp.json()

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

    def get_info_wallet(self):
        resp = self.call("GET", f"https://backend.gas.zip/v2/monadEligibility/{self.address}")
        return resp

    def claim(self):
        info_wallet = self.get_info_wallet()

        if info_wallet["eligibility"] == "UNCLAIMED":
            tier = 0

            if info_wallet["num_deposits"] >= 10: tier = 10
            elif info_wallet["num_deposits"] >= 25: tier = 25
            elif info_wallet["num_deposits"] >= 50: tier = 50
            elif info_wallet["num_deposits"] >= 100: tier = 100

            resp = self.call("GET", f"https://backend.gas.zip/v2/monadEligibility/{self.address}?claim=true&tier={tier}")
            
            return True

        else:
            logger.warning(f"{self.acc_name} eligibility: {info_wallet['eligibility']}")


    def bridge_for_transaction(self, amount, chain_out):
        amount_wei = self.gwei_to_wei(amount)

        resp = self.call("GET", f"https://backend.gas.zip/v2/quotes/{self.chain_id}/{amount_wei}/{chain_out.chain_id}?from={self.address}&to={self.address}")

        tx = {
            "chainId": self.chain_id,
            "data": resp["calldata"],
            "from": self.address,
            "nonce": self.nonce(),
            "to": "0x391E7C679d29bD940d63be94AD22A25d25b5A604",
            "value": hex(amount_wei)
        }

        return self.send_transaction(tx, f"bridge gas.zip {self.chain.chain} ETH > {chain_out.chain} ETH ({amount} ETH)")

