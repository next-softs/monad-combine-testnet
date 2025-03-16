from contracts.default import Default
from utils.encode import get_data_byte64
from models.chains import Chains

from bs4 import BeautifulSoup as bs



class MorkieNFT(Default):
    def __init__(self, account):
        super().__init__(account.private_key, Chains.Monad.rpc, [], "", account.proxy)

    def get_nfts(self):
        resp = self.session.get("https://morkie.xyz/")
        soup = bs(resp.text, "html.parser")

        nft_urls = []
        items = soup.find_all("article")
        for item in items:
            a = item.find("a")
            img = item.find_all("img")
            if a and img and "monad" in img[-1].get("src"):
                nft_urls.append("https://morkie.xyz" + a.get("href"))

        nfts = []
        for nft_url in nft_urls:
            resp = self.session.get(nft_url)
            soup = bs(resp.text, "html.parser")

            nft_name = soup.find("h4").text
            nfts.append({
                "nft": nft_name,
                "address": soup.find_all("article")[1].find("span").text,
                "amount": float(soup.find("h2").text.split()[0])
            })

        return nfts

    def mint(self, nft):
        data = data = get_data_byte64("0x84bb1e42", self.address, 1, "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", hex(self.gwei_to_wei(nft["amount"])),
                                      hex(192), 160, 80, "", "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff", "", "", "")

        tx = {
            "chainId": self.chain_id,
            "data": data,
            "from": self.address,
            "nonce": self.nonce(),
            "to": nft["address"],
            "value": hex(self.gwei_to_wei(nft["amount"]))
        }

        return self.send_transaction(tx, f"mint {nft['nft']}")
