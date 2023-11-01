from Class_Account import Account
from web3 import Web3
import time
from data import coins,contracts
from ABI import ERC20_ABI, ZKSWAP_ABI

class ZKswap(Account):
    def __int__(self, rpc,mnemonic):
        super().__init__(rpc,mnemonic)

    def swapTokenToToken(self, from_token_address, to_token_address,amount):

        if from_token_address == '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91':
            from_token_balance = self.web3.to_wei(amount, 'ether')
            from_token_allowance = 10 ** 20
        else:
            from_token_balance, from_token_allowance = self.get_token_balance(token_address=from_token_address,contract_address=contracts['ZKswap_address'],abi=ERC20_ABI)
        flag = 1
        while flag == 1:

            if from_token_allowance >= from_token_balance:

                start_time = int(time.time()) + 180
                addresses = [from_token_address, to_token_address]
                contract = self.web3.eth.contract(contracts['ZKswap_address'], abi=ZKSWAP_ABI)
                amountOut = contract.functions.getAmountsOut(from_token_balance, addresses).call()
                txn = self.txn()
                txn.update({'nonce': self.web3.eth.get_transaction_count(self.from_address)})
                if from_token_address == '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91':

                    txn.update({'value': from_token_balance})
                    transaction = contract.functions.swapExactETHForTokens(amountOut[1], addresses, self.from_address,start_time).build_transaction(txn)
                else:

                    if to_token_address == '0x5AEa5775959fBC2557Cc8789bC1bf90A239D9a91':

                        transaction = contract.functions.swapExactTokensForETH(amountOut[0], amountOut[1],addresses, self.from_address,start_time).build_transaction(txn)
                    else:

                        transaction = contract.functions.swapExactTokensForTokens(amountOut[0], amountOut[1],addresses, self.from_address,start_time).build_transaction(txn)

                signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
                hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
                txn_status = self.wait_tx_finished(hash=hash, max_wait_time=210)
                if txn_status == 1:

                    print(f'Хэш свапа из токена в токен: {hash.hex()}')
                    flag = 0
                else:

                    print(f'Не свапнули')
                    flag = 0
            else:

                self.approve(token_address=from_token_address,contract_address=contracts['ZKswap_address'])
                token_balance, allowance = self.get_token_balance(token_address=from_token_address,contract_address=contracts['ZKswap_address'],abi=ERC20_ABI)
                print(allowance)

    def ZKswapTokenToToken(self, from_token, to_token, amount):
        self.swapTokenToToken(from_token_address=Web3.to_checksum_address(coins[from_token]),to_token_address=Web3.to_checksum_address(coins[to_token]),amount=amount)


