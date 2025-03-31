from tenacity import retry, stop_after_attempt, wait_fixed

from contracts.default import Default
from utils.encode import get_data_byte64, split_data
from models.chains import Chains
from models.coins import Coins

import time


class OctoExchange(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "0xb6091233aAcACbA45225a2B2121BBaC807aF4255", account.proxy)

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    def call_api(self, method, url, **kwargs):
        resp = self.session.request(method, url, timeout=10, **kwargs)

        if resp.status_code != 200:
            raise Exception(f"[{resp.status_code}] {resp.text} {url}")

        return resp.json()

    def get_out_amount(self, in_token, out_token, in_amount):
        data = get_data_byte64("0xd06ca61f", hex(self.gwei_to_wei(in_amount, self.decimals(in_token.address))), "40", "2", in_token.address, out_token.address)
        # print(data)
        resp = self.call_api("POST", self.rpc, json={"jsonrpc": "2.0", "id": 1, "method": "eth_call", "params": [{"data": data, "to": self.contract_address}, "latest"]})["result"]
        data = split_data(resp)
        return hex(int(int(data[-1], 16) * 0.95))


    def swap_mon_for_token(self, in_token, out_token, in_amount):
        out_amount = self.get_out_amount(in_token, out_token, in_amount)
        data = get_data_byte64("0x7ff36ab5", out_amount, "80", self.address, hex(int(time.time() + 600)), "2", in_token.address, out_token.address)

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": hex(self.gwei_to_wei(in_amount))
        }

        return self.send_transaction(tx, f"swap {in_amount} {in_token.coin} > {out_token.coin} (OctoExchange)")

    def swap_token_for_token(self, in_token, out_token, in_amount):
        approved_amount = self.get_allowance(in_token.address, self.contract_address)

        if in_amount > approved_amount:
            self.approve(
                spender=self.contract_address,
                token_address=in_token.address,
                amount=in_amount,
            )

        out_amount = self.get_out_amount(in_token, out_token, in_amount)
        data = get_data_byte64("0x18cbafe5", hex(self.gwei_to_wei(in_amount, self.decimals(in_token.address))), out_amount, hex(160), self.address, hex(int(time.time() + 600)), "2", in_token.address, out_token.address)

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address
        }

        return self.send_transaction(tx, f"swap {in_amount} {in_token.coin} > {out_token.coin} (OctoExchange)")


    def swap(self, in_token, out_token, in_amount):
        # mon swap token
        if in_token.coin == "MON":
            in_token = Coins.WMON

            return self.swap_mon_for_token(in_token, out_token, in_amount)

        # token swap token
        else:
            if out_token.coin == "MON":
                out_token = Coins.WMON

            return self.swap_token_for_token(in_token, out_token, in_amount)

