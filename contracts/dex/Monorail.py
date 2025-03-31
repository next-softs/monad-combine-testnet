from tenacity import retry, stop_after_attempt, wait_fixed

from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
from models.coins import Coins


class Monorail(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "0xC995498c22a012353FAE7eCC701810D673E25794", account.proxy)

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    def call_api(self, method, url, **kwargs):
        resp = self.session.request(method, url, timeout=10, **kwargs)

        if resp.status_code != 200:
            raise Exception(f"[{resp.status_code}] {resp.text} {url}")

        return resp.json()

    def swap(self, in_token, out_token, in_amount):
        if in_token.coin not in ["MON", "WMON"]:
            approved_amount = self.get_allowance(in_token.address, self.contract_address)
            if in_amount > approved_amount:
                self.approve(
                    spender=self.contract_address,
                    token_address=in_token.address,
                    amount=in_amount,
                )

        transaction = self.call_api("GET", "https://testnet-pathfinder-v2.monorail.xyz/v1/quote", params={
            "amount": in_amount,
            "from": in_token.address,
            "to": out_token.address,
            "slippage": 100,
            "deadline": 300,
            "source": "fe3",
            "sender": self.address
        })["transaction"]


        tx = {
            "chainId": self.chain_id,
            "data": transaction["data"],
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": transaction["value"]
        }

        return self.send_transaction(tx, f"swap {in_amount} {in_token.coin} > {out_token.coin} (Monorail)")
