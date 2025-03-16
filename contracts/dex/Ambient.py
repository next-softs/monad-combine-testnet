from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
from models.coins import Coins


class Ambient(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "0x88b96af200c8a9c35442c8ac6cd3d22695aae4f0", account.proxy)

    def approve(self, spender, address_to="", amount=0):
        data = get_data_byte64("0x095ea7b3",
                               spender,
                               hex(self.gwei_to_wei(amount)))

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": address_to
        }

        if address_to: tx.update({"to": address_to})

        try:
            status = self.send_transaction(tx, "approve")
            return status

        except Exception as e:
            logger.error(f"{self.acc_name} {e}")

        return False

    def swap(self, amount):
        approved_amount = self.get_allowance(Coins.ETH.address, self.contract_address)

        if amount > approved_amount:
            self.approve(
                spender=self.contract_address,
                address_to=Coins.ETH.address,
                amount=self.token_balance(Coins.ETH.address),
            )

        data = get_data_byte64("0xa15112f9", 1, 40, 140, "",
                               Coins.ETH.address, hex(36000), "", "",
                               hex(self.gwei_to_wei(amount)), "", 10001,
                               hex(self.gwei_to_wei(amount*0.98)), "")

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address
        }

        return self.send_transaction(tx, f"swap {amount} ETH > MON")
