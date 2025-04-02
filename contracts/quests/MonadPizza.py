import random, time, json, datetime

from eth_account.messages import encode_defunct
from contracts.default import Default
from models.chains import Chains

from utils.logs import logger
from utils.encode import get_data_byte64, split_data
from utils.file_manager import get_json
from config import *


class MonadPizza(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, get_json("abis/monad_pizza"), "0x637F93AAA322880d89631Df79619c9e4a0d6D0e3", account.proxy)
        self.contracts_badges = self.w3.eth.contract(address="0x212ad945e95A74a7164993e5e4c2BD884E9672e7", abi=get_json("abis/monad_pizza_badges"))

    def click_cooldown(self):
        return self.contract.functions.clickCooldown().call()

    def check_register(self):
        return self.contract.functions.checkRegistration(self.address).call()

    def get_time_active_boost(self):
        return self.contract.functions.getAutoClickerStatus(self.address).call()[0]

    def points_balance(self):
        return self.contract.functions.getUserStats(self.address).call()[0]

    def register(self, referrer_address="0x0000000000000000000000000000000000000000"):
        if not self.check_register():
            if MonadPizzaSettings.referrer_address:
                referrer_address = random.choice(MonadPizzaSettings.referrer_address)

            data = self.contract.encode_abi("registration", args=(referrer_address,))

            tx = {
                "chainId": self.chain_id,
                "data": data,
                "from": self.address,
                "nonce": self.nonce(),
                "to": self.contract_address
            }

            return self.send_transaction(tx, "register")

    def can_click(self):
        return self.contract.functions.canClick(self.address).call()

    def click(self):
        tx = {
            "chainId": self.chain_id,
            "data": "0x7d55923d",
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address
        }

        self.send_transaction(tx, "click")
        time.sleep(1)

        return self.can_click()

    def badge_balance(self, tokenId):
        return int(self.gwei_to_wei(self.token_balance_erc1155("0x212ad945e95A74a7164993e5e4c2BD884E9672e7", tokenId)))

    def start_auto_clicker(self):
        amount = self.contract.functions.autoClickerPrice().call()

        tx = {
            "chainId": self.chain_id,
            "data": "0xa3bcd931",
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": hex(amount)
        }

        self.send_transaction(tx, f"start auto clicker")
        time.sleep(1)

        return self.get_time_active_boost()

    def check_battle_pass(self):
        return self.contract.functions.checkBattlePass(self.address).call()

    def buy_battle_pass(self):
        amount = self.contract.functions.battlePassPrice().call()

        tx = {
            "chainId": self.chain_id,
            "data": "0xa7757f51",
            "from": self.address,
            "nonce": self.nonce(),
            "to": self.contract_address,
            "value": hex(amount)
        }

        return self.send_transaction(tx, "buy battle pass")

    def get_user_info(self):
        resp = self.contract.functions.getUserStats(self.address).call()

        return {
            "points": resp[0],
            "referrals": resp[1],
            "battlePassCount": resp[2],
            "isRegistered": resp[3],
            "pendingReferralRewards": resp[4],
            "totalReferralPoints": resp[5],
            "activeNFTBonusIds": resp[6],
            "activeTokenBonusIds": resp[7],
        }

    def claim_badge(self, badge, amount=0.005, name=""):
        tx = {
            "chainId": self.chain_id,
            "data": get_data_byte64("0xa0712d68", hex(badge)),
            "from": self.address,
            "nonce": self.nonce(),
            "to": "0x212ad945e95A74a7164993e5e4c2BD884E9672e7",
            "value": hex(amount)
        }

        return self.send_transaction(tx, f"claim badge {name} {badge}")

    def get_info_badges(self):
        resp = self.contracts_badges.functions.getNftList(self.address).call()

        badges = []

        for badge in resp:
            badges.append({
                "name": badge[0],
                "price": badge[1],
                "requiredPoints": badge[2],
                "requiredReferrals": badge[3],
                "isPublic": badge[4],
                "isAvailable": badge[5],
                "isMint": badge[6],
                "tokenId": badge[7],
                "nftType": badge[8],
            })

        return badges
