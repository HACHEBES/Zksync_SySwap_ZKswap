from Class_ZKswap import ZKswap
from RPC import *
from Class_SySwap import SySwap


seeds = []

testnet_rpc = Rpc['ZKSync_rpc']
with open('seeds.txt','r') as file:
    for line in file:
        seeds.append(line.strip())

for i in range(len(seeds)):

    seed = seeds[i]
    amount = 0.00001
    ZKswap_1 = ZKswap(rpc=testnet_rpc,mnemonic=seed)
    SySwap_1 = SySwap(rpc=testnet_rpc,mnemonic=seed)
    ZKswap_1.ZKswapTokenToToken(from_token='USDT',to_token='ETH',amount=amount)
    SySwap_1.SySTokenToToken(from_token='ETH',to_token='USDC',amount=amount)