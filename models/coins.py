from web3 import Web3

class CoinInfo:
    def __init__(self, coin, address):
        self.coin = coin
        self.address = Web3().to_checksum_address(address)

    def __repr__(self):
        return self.coin

class Coins:
    MON = CoinInfo(coin="MON", address="0x0000000000000000000000000000000000000000")
    WMON = CoinInfo(coin="WMON", address="0x760AfE86e5de5fa0Ee542fc7B7B713e1c5425701")

    ETH = CoinInfo(coin="ETH", address="0x836047a99e11F376522B447bffb6e3495Dd0637c")
    WETH = CoinInfo(coin="WETH", address="0xB5a30b0FDc5EA94A52fDc42e3E9760Cb8449Fb37")
    WBTC = CoinInfo(coin="WBTC", address="0xcf5a6076cfa32686c0Df13aBaDa2b40dec133F1d")

    USDC = CoinInfo(coin="USDC", address="0xf817257fed379853cDe0fa4F97AB987181B1E5Ea")
    USDT = CoinInfo(coin="USDT", address="0x88b8e2161dedc77ef4ab7585569d2415a1c1055d")

    DAK = CoinInfo(coin="DAK", address="0x0f0bdebf0f83cd1ee3974779bcb7315f9808c714")
    MUK = CoinInfo(coin="MUK", address="0x989d38aeed8408452f0273c7d4a17fef20878e62")
    CHOG = CoinInfo(coin="CHOG", address="0xE0590015A873bF326bd645c3E1266d4db41C4E6B")
    YAKI = CoinInfo(coin="YAKI", address="0xfe140e1dCe99Be9F4F15d657CD9b7BF622270C50")
