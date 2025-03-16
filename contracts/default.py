from web3 import Web3
from decimal import Decimal

from config import *
from utils.logs import logger
from utils.session import create_session
from utils.encode import get_data_byte64, data_decoder

import random, time


class Default:
    def __init__(self, private_key, rpc, abi=[], contract_address=None, proxy=None):
        self.session = create_session(proxy)
        self.w3 = Web3(Web3.HTTPProvider(rpc, session=self.session))
        self.chain_id = self.w3.eth.chain_id

        self.private_key = private_key
        self.address = self.w3.eth.account.from_key(self.private_key).address
        self.acc_name = f"{self.address[:5]}..{self.address[-5:]}"

        if contract_address:
            self.contract_address = self.w3.to_checksum_address(contract_address)
            self.contract = self.w3.eth.contract(address=self.contract_address, abi=abi)

        self.gwei = 18
        self.erc20_abi = [{'constant': True, 'inputs': [{'name': '_owner', 'type': 'address'}], 'name': 'balanceOf', 'outputs': [{'name': 'balance', 'type': 'uint256'}], 'type': 'function'}, {'constant': True, 'inputs': [], 'name': 'decimals', 'outputs': [{'name': '', 'type': 'uint8'}], 'type': 'function'}, {'constant': True, 'inputs': [{'name': '_owner', 'type': 'address'}, {'name': '_spender', 'type': 'address'}], 'name': 'allowance', 'outputs': [{'name': 'remaining', 'type': 'uint256'}], 'type': 'function'}]
        self.uniswap_v2_router_abi = [{"constant":True,"inputs":[{"name":"amountIn","type":"uint256"},{"name":"path","type":"address[]"}],"name":"getAmountsOut","outputs":[{"name":"","type":"uint256[]"}],"payable":False,"stateMutability":"view","type":"function"}]


        self.inf = 115792089237316195423570985008687907853269984665640564039457584007913129639935

    def sleep(self, delay):
        timeout = random.randint(*delay)
        logger.info(f"{self.acc_name} ожидаем {timeout} сек.")
        time.sleep(timeout)

    def gwei_to_wei(self, value_in_gwei, gwei=0):
        gwei = gwei if gwei != 0 else self.gwei
        return int(Decimal(str(value_in_gwei)) * Decimal(10**gwei))

    def wei_to_gwei(self, value_in_wei, gwei=0):
        gwei = gwei if gwei != 0 else self.gwei
        return round(Decimal(str(value_in_wei)) / Decimal(10**gwei), gwei)

    def send_transaction(self, tx, desc=""):
        try:
            if "gas" not in tx: tx.update({"gas": hex(int(self.w3.eth.estimate_gas(tx) * 1.5))})
            if "gasPrice" not in tx: tx.update({"gasPrice": hex(int(self.w3.eth.gas_price * 1.2))})

            signed_txn = self.w3.eth.account.sign_transaction(tx, private_key=self.private_key)
            raw_tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
            data = self.w3.eth.wait_for_transaction_receipt(raw_tx_hash, timeout=300)

            if data.get("status") is not None and data.get("status") == 1:
                logger.success(f'{self.acc_name} {desc + " " if desc else ""}{data.get("transactionHash").hex()}')
                return True
            else:
                logger.error(f'{self.acc_name} {desc + " " if desc else ""}{data.get("transactionHash").hex()}')

        except Exception as e:
            err = data_decoder(e.data)
            if not err: err = e

            logger.error(f'{self.acc_name} {desc + " " if desc else ""}| Error: {err}')

        return False

    def nonce(self):
        return hex(self.w3.eth.get_transaction_count(self.address))

    def get_allowance(self, token_address, spender=None):
        contract_address = self.w3.to_checksum_address(token_address)
        contract_instance = self.w3.eth.contract(address=contract_address, abi=self.erc20_abi)

        amount = contract_instance.functions.allowance(self.address, self.w3.to_checksum_address(spender)).call()
        if amount == self.inf:
            return int(self.inf)

        return float(self.wei_to_gwei(amount))

    def approve(self, spender, token_address, amount=0):
        data = get_data_byte64("0x095ea7b3",
                               spender,
                               hex(self.gwei_to_wei(amount)) if amount != 0 else "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff")

        tx = {
            "chainId": self.w3.eth.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce()
        }

        if token_address: tx.update({"to": token_address})

        status = self.send_transaction(tx, "approve")
        return status

    def decimals(self, token_address):
        contract_instance = self.w3.eth.contract(address=token_address, abi=self.erc20_abi)
        return contract_instance.functions.decimals().call()

    def balance(self):
        return self.wei_to_gwei(self.w3.eth.get_balance(self.address))

    def token_balance(self, token_address):
        try:
            contract_instance = self.w3.eth.contract(address=token_address, abi=self.erc20_abi)
            return self.wei_to_gwei(contract_instance.functions.balanceOf(self.address).call(), self.decimals(token_address))
        except Exception as err:
            return self.token_balance_erc1155(token_address)

        return 0

    def token_balance_erc1155(self, token_address, tokenId=0):
        try:
            contract_instance = self.w3.eth.contract(address=token_address, abi=[{"constant": True, "inputs":
                [{"name": "account", "type": "address"}, {"name": "id", "type": "uint256"}], "name": "balanceOf", "outputs": [{"name": "", "type": "uint256"}], "stateMutability": "view","type": "function"}])
            return self.wei_to_gwei(contract_instance.functions.balanceOf(self.address, tokenId).call())
        except Exception as err:
            logger.error(f"{self.acc_name} error token_balance {err}")

        return 0

    def out_amount_min_swap(self, router_address, path, amount_in):
        router_contract = self.w3.eth.contract(address=router_address, abi=self.uniswap_v2_router_abi)
        amounts_out = router_contract.functions.getAmountsOut(amount_in, path).call()

        amount_out = amounts_out[-1]

        return amount_out