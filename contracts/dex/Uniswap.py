from tenacity import retry, stop_after_attempt, wait_fixed
from eth_account.messages import encode_typed_data

from contracts.default import Default
from utils.encode import get_data_byte64
from utils.logs import logger

from models.chains import Chains
from models.coins import Coins
import time


class Uniswap(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "", account.proxy)
        self.api_key = ""

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    def call_api(self, url, params):
        params["gasStrategies"] = [{"limitInflationFactor": 1.15,"displayLimitInflationFactor": 1.15,"priceInflationFactor": 1.5,"percentileThresholdFor1559Fee": 75,"minPriorityFeeGwei": 2,"maxPriorityFeeGwei": 9}]

        headers = self.session.headers
        headers["x-api-key"] = self.api_key

        resp = self.session.post(url, json=params, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"[{resp.status_code}] {resp.text} {url}")

        return resp.json()

    def get_api_key(self):
        return "JoyCGj29tT4pymvhaGciK4r1aIPvqW6W53xT1fwo"
        resp = self.session.get("https://app.uniswap.org/static/js/main.5ff8e115.js")
        return resp.text.split('REACT_APP_TRADING_API_KEY:"')[1].split('"')[0]

    def get_quote(self, in_token, out_token, in_amount):
        params = {
            "amount": str(in_amount),
            "swapper": self.address,
            "tokenIn": in_token,
            "tokenInChainId": self.chain_id,
            "tokenOut": out_token,
            "tokenOutChainId": self.chain_id,
            "type": "EXACT_INPUT",
            "urgency": "normal",
            "protocols": ["V2"],
            "autoSlippage": "DEFAULT"
        }

        return self.call_api("https://trading-api-labs.interface.gateway.uniswap.org/v1/quote", params)

    def get_data(self, quote, permitData={}, signature=None):
        params = {
            "quote": quote,
            "simulateTransaction": True,
            "refreshGasPrice": True,
            "gasStrategies": [],
            "urgency": "normal"
        }

        if permitData: params["permitData"] = permitData
        if signature: params["signature"] = signature

        return self.call_api("https://trading-api-labs.interface.gateway.uniswap.org/v1/swap", params)

    def sign(self, message):
        message_sign = {
            "types": message["types"],
            "domain": message["domain"],
            "primaryType": "PermitSingle",
            "message": message["values"]
        }

        message_sign["types"]["EIP712Domain"] = [{"name": "name","type": "string"}, {"name": "chainId","type": "uint256"},{"name": "verifyingContract","type": "address"}]

        message_sign["domain"]["chainId"] = str(message_sign["domain"]["chainId"])
        message_sign["domain"]["verifyingContract"] = message_sign["domain"]["verifyingContract"].lower()

        message_sign["message"]["details"]["token"] = message_sign["message"]["details"]["token"].lower()
        message_sign["message"]["spender"] = message_sign["message"]["spender"].lower()

        signable_message = encode_typed_data(full_message=message_sign)
        signed = self.w3.eth.account.sign_message(signable_message=signable_message,private_key=self.private_key)
        signature = signed.signature.hex()

        return "0x" + signature

    def swap(self, in_token, out_token, in_amount):
        try:
            if in_token.coin in ["MON", "WMON"]: in_token = Coins.WMON

            self.api_key = self.get_api_key()
            amount_wei = self.gwei_to_wei(in_amount, self.decimals(in_token.address))

            # token_for_token
            if in_token.coin not in ["MON", "WMON"]:
                allowed = self.get_allowance(in_token.address, "0x000000000022D473030F116dDEE9F6B43aC78BA3")

                if allowed < in_amount:
                    self.approve(spender="0x000000000022D473030F116dDEE9F6B43aC78BA3", token_address=in_token.address)
                    time.sleep(3)

                quote_data = self.get_quote(in_token.address, out_token.address, amount_wei)

                quote = quote_data["quote"]
                permitData = quote_data["permitData"]

                sign = self.sign(permitData) if permitData else None
                data = self.get_data(quote, permitData, sign)["swap"]

            # mon_for_token
            else:
                quote = self.get_quote(Coins.MON.address, out_token.address, amount_wei)["quote"]
                data = self.get_data(quote)["swap"]

            tx = {
                "chainId": data["chainId"],
                "data": data["data"],
                "from": self.address,
                "nonce": self.nonce(),
                "to": self.w3.to_checksum_address(data["to"]),
                "value": hex(int(data["value"], 16)),

            }

            if out_token.coin in ["MON", "WMON"]: decimals = 0
            else: decimals = self.decimals(out_token.address)

            return self.send_transaction(tx, f"swap {in_amount} {in_token.coin} > {self.wei_to_gwei(quote['output']['amount'], decimals)} {out_token.coin} (Uniswap)")
        except Exception as err:
            logger.error(f"{self.acc_name} swap unswap {err}")

        return False
