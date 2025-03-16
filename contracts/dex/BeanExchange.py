from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains
from models.coins import Coins
import time


class BeanExchange(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "0xCa810D095e90Daae6e867c19DF6D9A8C56db2c89", account.proxy)


    def swap_mon_for_token(self, in_token, out_token, in_amount):
        in_amount_wei = self.gwei_to_wei(in_amount)
        out_amount = self.out_amount_min_swap(router_address=self.contract_address, path=[in_token.address, out_token.address], amount_in=in_amount_wei)

        data = get_data_byte64("0x7ff36ab5", hex(int(out_amount * 0.9)), hex(128), self.address, hex(int(time.time()+600)), hex(2), in_token.address, out_token.address)

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": hex(in_amount_wei),

        }

        return self.send_transaction(tx, f"swap {in_amount} {in_token.coin} > {self.wei_to_gwei(out_amount, self.decimals(out_token.address))} {out_token.coin} (BeanExchange)")

    def swap_token_for_token(self, in_token, out_token, in_amount):
        allowed = self.get_allowance(in_token.address, self.contract_address)
        if allowed < in_amount:
            self.approve(
                spender=self.contract_address,
                token_address=in_token.address
            )

        in_amount_wei = self.gwei_to_wei(in_amount, self.decimals(in_token.address))
        out_amount = self.out_amount_min_swap(router_address=self.contract_address, path=[in_token.address, out_token.address], amount_in=in_amount_wei)

        data = get_data_byte64("0x18cbafe5", hex(int(in_amount_wei)), hex(int(out_amount * 0.9)), hex(160), self.address, hex(int(time.time()+600)), hex(2), in_token.address, out_token.address)

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address
        }

        return self.send_transaction(tx, f"swap {in_amount} {in_token.coin} > {self.wei_to_gwei(out_amount, self.decimals(out_token.address))} {out_token.coin} (BeanExchange)")

    def swap(self, in_token, out_token, in_amount):
        if in_token.coin == "MON": in_token = Coins.WMON
        if out_token.coin == "MON": out_token = Coins.WMON

        if in_token.coin == "WMON":
            return self.swap_mon_for_token(Coins.WMON, out_token, in_amount)
        else:
            return self.swap_token_for_token(in_token, out_token, in_amount)