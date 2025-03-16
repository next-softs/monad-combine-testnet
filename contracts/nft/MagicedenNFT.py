from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains


class MagicedenNFT(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "", account.proxy)

    def mint(self, nft):
        data = data = get_data_byte64("0x9b4f3af5", self.address, "", 1, 80, "")

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": nft["address"],
            "value": hex(self.gwei_to_wei(nft["amount"]))
        }

        return self.send_transaction(tx, f"mint {nft['address']}")
