
class Chain:
    def __init__(self, chain, rpc, chain_id=None):
        self.chain = chain
        self.rpc = rpc

        self.chain_id = chain_id

class Chains:
    Sepolia = Chain(chain="Sepolia", rpc="https://sepolia.drpc.org")
    Monad = Chain(chain="Monad", rpc="https://testnet-rpc.monad.xyz/")

    OP = Chain(chain="OP", rpc="https://optimism.llamarpc.com", chain_id=10)
    Base = Chain(chain="Base", rpc="https://base.llamarpc.com", chain_id=8453)
    ARB = Chain(chain="ARB", rpc="https://arbitrum.llamarpc.com", chain_id=42161)
    Unichain = Chain(chain="Unichain", rpc="https://unichain.drpc.org", chain_id=130)
