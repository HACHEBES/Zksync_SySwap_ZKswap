from Class_Account import Account
from web3 import Web3
import time
from data import coins,contracts
from ABI import ERC20_ABI, SYNCSWAP_CLASSIC_POOL_ABI,router_ABI,SYNCSWAP_CLASSIC_POOL_DATA_ABI
from eth_abi import abi


class SySwap(Account):
    def __int__(self, rpc,mnemonic):
        super().__init__(rpc,mnemonic)

    def SySTokenToToken(self,from_token, to_token, amount):

        if from_token == 'ETH':
            amount = Web3.to_wei(amount, 'ether')
        else:
            from_token_balance, allowance = self.get_token_balance(token_address = coins[from_token],contract_address = contracts['syncswap_address_router'], abi = ERC20_ABI )
            amount = from_token_balance

        start_time = int(time.time()) + 180
        syncswap_contract_pool = self.web3.eth.contract(contracts['syncswap_address'],abi = SYNCSWAP_CLASSIC_POOL_ABI )
        pool_address = syncswap_contract_pool.functions.getPool(self.web3.to_checksum_address(coins[from_token]),self.web3.to_checksum_address(coins[to_token])).call()
        min_amount_out = self.get_min_amount_out(pool_address, coins[to_token], amount)

        swapData = abi.encode(['address', 'address', 'uint8'], [self.web3.to_checksum_address(coins[from_token]), self.from_address, 1])

        steps = [{
            'pool': pool_address,
            'data': swapData,
            'callback': coins['ZERO_ADDRESS'],
            'callbackData': '0x',
        }]

        if from_token == 'ETH':
            path = [{
                'steps': steps,
                'tokenIn': coins['ZERO_ADDRESS'],
                'amountIn': amount,
            }]
        else:
            path = [{
                'steps': steps,
                'tokenIn': coins[from_token],
                'amountIn': amount,
            }]

        syncswap_contract = self.web3.eth.contract(address=contracts['syncswap_address_router'], abi=router_ABI)

        txn = self.txn()
        txn.update({'nonce': self.web3.eth.get_transaction_count(self.from_address)})

        if from_token == 'ETH':
            txn.update({'value': amount})
        else:
            if allowance <= amount:
                self.approve(token_address = coins[from_token], contract_address = contracts['syncswap_address_router'])

        transaction = syncswap_contract.functions.swap(path, min_amount_out, start_time).build_transaction(txn)
        signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
        hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_status = self.wait_tx_finished(hash = hash, max_wait_time = 210)

        if txn_status == 1:
            print(f'Хэш свапа в токен: {hash.hex()}')
        else:
            print(f'Не свапнули')

    def get_min_amount_out(self, pool_address: str, token_address: str, amount: int):
        pool_contract = self.web3.eth.contract(pool_address, abi=SYNCSWAP_CLASSIC_POOL_DATA_ABI)
        min_amount_out =pool_contract.functions.getAmountOut(token_address,amount,self.from_address).call()
        return int(min_amount_out)