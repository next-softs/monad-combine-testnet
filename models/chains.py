
class Chain:
    def __init__(self, chain, rpc):
        self.chain = chain
        self.rpc = rpc

class Chains:
    Sepolia = Chain(chain="Sepolia", rpc="https://sepolia.drpc.org")
    Monad = Chain(chain="Monad", rpc="https://testnet-rpc.monad.xyz/")

    OP = Chain(chain="OP", rpc="https://optimism.llamarpc.com")
    Base = Chain(chain="Base", rpc="https://base.llamarpc.com")
    ARB = Chain(chain="ARB", rpc="https://arbitrum.llamarpc.com")
