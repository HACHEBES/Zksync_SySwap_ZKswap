from web3 import Web3
import time
from web3.exceptions import TransactionNotFound
from data import *
from ABI import*
from RPC import*
class Account:

    def __init__(self,rpc, mnemonic):

        self.web3 = Web3(Web3.HTTPProvider(rpc))
        self.web3.eth.account.enable_unaudited_hdwallet_features()
        self.acc = self.web3.eth.account.from_mnemonic(mnemonic)
        self.private_key = self.acc._private_key
        self.from_address = self.acc.address

    def wait_tx_finished(self,hash,max_wait_time):

        start_time = time.time()
        while True:
            try:
                receipts = self.web3.eth.get_transaction_receipt(hash)
                status = receipts.get("status")
                if status == 1:
                    return 1
                elif status is None:
                    time.sleep(0.3)
                else:
                    return 0
            except TransactionNotFound:
                if time.time() - start_time > max_wait_time:
                    print(f'FAILED TX: {hash}')
                    return 0
                time.sleep(1)

    def txn(self):

        txn = {
            'chainId': self.web3.eth.chain_id,
            'gasPrice': self.web3.eth.gas_price,
            'from': self.from_address
        }
        return txn

    def approve(self, token_address,contract_address):

        txn = self.txn().update({'nonce': self.web3.eth.get_transaction_count(self.from_address)})
        approve_amount = 2 ** 256 - 1
        token_contract = self.web3.eth.contract(token_address, abi=ERC20_ABI)
        transaction = token_contract.functions.approve(contract_address, approve_amount).build_transaction(txn)
        signed_txn = self.web3.eth.account.sign_transaction(transaction, self.private_key)
        hash = self.web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_status = self.wait_tx_finished(hash=hash, max_wait_time=210)
        if txn_status == 1:
            print(f'Хэш апрува: {hash.hex()}')
        else:
            print(f'Фрэди фаз биар не вывели(')

    def token_to_wei(self, contract_address, amount):

        contract = self.web3.eth.contract(contract_address, abi=ERC20_ABI)
        token_decimals = contract.functions.decimals().call()
        token_wei = amount * 10 ** token_decimals
        return token_wei

    def get_token_balance(self, token_address, contract_address, abi):  # Функция возвращает баланс введенного токена в WEI и количество токенов которым мы дали апрув

        token_contract = self.web3.eth.contract(address=token_address, abi=abi)
        balance_of_token = token_contract.functions.balanceOf(self.from_address).call()
        allowance = token_contract.functions.allowance(self.from_address, contract_address).call()
        return balance_of_token, allowance


