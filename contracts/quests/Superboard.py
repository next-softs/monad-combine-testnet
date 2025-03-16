from tenacity import retry, stop_after_attempt, wait_fixed

import urllib.parse
import random, time, json, re
from bs4 import BeautifulSoup as bs

from eth_account.messages import encode_defunct
from datetime import datetime, timezone, timedelta
from contracts.default import Default
from models.chains import Chains

from utils.logs import logger
from config import SuperboardSettings


class Superboard(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "", account.proxy)

        self.auth_token = ""
        self.networks = {}

    @retry(stop=stop_after_attempt(5), wait=wait_fixed(3))
    def call(self, method, url, retJson=True, **kwargs):
        resp = self.session.request(method, url, timeout=10, **kwargs)

        if retJson:
            resp = resp.text
            fixed_json = re.sub(r',\s*}', '}', resp)
            fixed_json = re.sub(r',\s*\]', ']', fixed_json)
            return json.loads(fixed_json)

        return json.text


    def register(self, payload, sign):
        params = {
            "0": {
                "wallets": [{
                    "walledId": 10,
                    "walletName": "Rabby",
                    "description": "",
                    "networks": [{
                        "networkId": 1,
                        "address": self.address,
                        "family": "ETHEREUM",
                        "verify": {
                          "header": {
                            "t": "eip191"
                          },
                          "payload": payload,
                          "signature": sign
                        }}]
                }],
                "uiProperties": {
                "avatar": "",
                "headerImage": "",
                "language": "ENGLISH"
                }
            }}

        resp = self.call("POST", "https://api-prod.superboard.xyz/api/trpc/user.register?batch=1", json=params)
        logger.info(f"{self.acc_name} registered")

    def login(self):
        if self.auth_token:
            logger.success(f"{self.acc_name} logined")
            self.session.headers["authorization"] = f"Bearer {self.auth_token}"
            return True

        utc_time = datetime.now(timezone.utc)

        payload = {
            "domain": "superboard.xyz",
            "address": self.address,
            "statement": "Login to SuperBoard",
            "uri": "https://superboard.xyz",
            "version": "1",
            "chainId": 1,
            "nonce": str(random.randint(100000000000000000, 999999999999999999)),
            "issuedAt": utc_time.strftime('%Y-%m-%dT%H:%M:%S') + f".{utc_time.microsecond // 1000:03d}Z",
            "expirationTime": (utc_time + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%S.000Z')
        }

        message = (f"superboard.xyz wants you to sign in with your Ethereum account:\n"
                   f"{self.address}\n\n"
                   f"Login to SuperBoard\n\n"
                   f"URI: {payload['uri']}\n"
                   f"Version: {payload['version']}\n"
                   f"Chain ID: {payload['chainId']}\n"
                   f"Nonce: {payload['nonce']}\n"
                   f"Issued At: {payload['issuedAt']}\n"
                   f"Expiration Time: {payload['expirationTime']}")

        encoded_message = encode_defunct(text=message)
        signed_message = self.w3.eth.account.sign_message(encoded_message, private_key=self.private_key)

        sign = "0x" + signed_message.signature.hex()
        params = {"0": {"data": {"header": {"t": "eip191"}, "payload": payload, "signature": sign}, "networkId": 1, "network": "ETHEREUM", "family": "ETHEREUM"}}

        for i in range(5):
            resp = self.call("POST", "https://api-prod.superboard.xyz/api/trpc/auth.login?batch=1", json=params)[0]

            if "error" in resp and resp["error"]["message"] == "User not found":
                self.register(payload, sign)
            elif "result" in resp and resp["result"]["data"]["token"]:
                logger.success(f"{self.acc_name} logined")

                self.auth_token = resp["result"]["data"]["token"]
                self.session.headers["authorization"] = f"Bearer {self.auth_token}"

                for network in resp["result"]["data"]["wallets"][0]["userNetworks"]:
                    self.networks[network["networkId"]] = network["id"]

                return True
            else:
                raise Exception(f"{self.acc_name} error auth {resp}")

            time.sleep(3)

    def get_quests(self):
        data_input = {
            "0": {
                "page": 0,
                "limit": 10000,
                "sort": "asc",
                "entityBelongsTo": "QUEST",
                "entityType": "FLAG"
            }
        }

        data_input = urllib.parse.quote(json.dumps(data_input, separators=(",", ":")))

        resp = self.call("GET", f"https://api-prod.superboard.xyz/api/trpc/entity.getEntitiesWithQuests,treat.getUserTreat?batch=1&input={data_input}")[0]["result"]["data"]

        quests_data = []

        for quests in resp:
            for quest in quests["quests"]:
                if quest and (not SuperboardSettings.monad_only or "monad" in quest["description"].lower()):
                    quests_data.append(quest)

        return quests_data

    def execute_quest(self, quest):
        slug_input = urllib.parse.quote(json.dumps({"0": {"slug": quest["slug"]}}, separators=(",", ":")))
        quest_info = self.call("GET", f"https://api-prod.superboard.xyz/api/trpc/quest.getQuestBySlug?batch=1&input={slug_input}")[0]["result"]["data"]

        if "userQuest" not in quest_info:
            quest_info = self.call("POST", f"https://api-prod.superboard.xyz/api/trpc/quest.userTakeQuest?batch=1", json={"0": {"id": quest["id"], "userNetworkId": self.networks[1]}})
            quest_info = self.call("GET", f"https://api-prod.superboard.xyz/api/trpc/quest.getQuestBySlug?batch=1&input={slug_input}")[0]["result"]["data"]

        if "userQuest" not in quest_info:
            logger.warning(f"{self.acc_name} {quest['name']} не удалось начать выполнение квеста")
            return

        user_quest = quest_info["userQuest"][0]
        tasks_taken = [task["taskId"] for task in user_quest["tasksTaken"]]

        # выпоняем задания
        for task in quest_info["tasks"]:
            if task["id"] in tasks_taken:
                continue

            logger.info(f"{self.acc_name} выполняем заданые {task['name']}")

            verify_task = self.call("POST", "https://api-prod.superboard.xyz/api/trpc/task.userVerifyTask?batch=1", json={
                "0": {
                    "id": task["id"],
                    "userQuestId": user_quest["id"],
                    "userNetworkId": self.networks[task["networkId"]],
                    "answer": {
                        "userQuestId": user_quest["id"],
                        "userNetworkId": self.networks[task["networkId"]],
                        "id": task["id"]
                    }
                }})[0]

            if "error" in verify_task:
                logger.warning(f"{self.acc_name} {task['name']} {verify_task['error']['message']}")
                return
            else:
                logger.success(f"{self.acc_name} {task['name']} задание выполнено")
                self.sleep(SuperboardSettings.delay_task)

        # проверяем задание
        data_input = urllib.parse.quote(json.dumps({"0": {"id": user_quest["questId"]}}, separators=(",", ":")))
        verify_quest = self.call("GET", f"https://api-prod.superboard.xyz/api/trpc/quest.verifyUserQuestCompletion?batch=1&input={data_input}")[0]
        if "error" in verify_quest:
            logger.warning(f"{self.acc_name} {quest['name']} ошибка при верификации квеста {verify_quest['error']['message']}")
        elif verify_quest["result"]["data"]["status"] == "success":
            logger.success(f"{self.acc_name} {quest['name']} квест пройден")
        else:
            logger.warning(f"{self.acc_name} {quest['name']} {verify_quest}")

        # получаем награду
        claim_quest = self.call("POST", "https://api-prod.superboard.xyz/api/trpc/quest.userQuestClaimRewards?batch=1", json={"0": {"type": "Points", "questId": str(user_quest["questId"])}})[0]

        if "error" in claim_quest:
            if claim_quest['error']['message'] == "User already claimed the reward":
                logger.info(f"{self.acc_name} {quest['name']} награда за квест уже получена")
            else:
                logger.warning(f"{self.acc_name} {quest['name']} ошибка при получении награды {claim_quest['error']['message']}")

        elif claim_quest["result"]["data"]["status"] == "success":
            logger.success(f"{self.acc_name} {quest['name']} награда получена +{quest['rewardPoints']} Points")
            return True
        else:
            logger.warning(f"{self.acc_name} {quest['name']} {claim_quest}")
