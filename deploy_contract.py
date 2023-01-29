
import json
from web3 import Web3
import os

web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
# dev0

account = '0xe5Dc96369d2B1AE7DC82eD5783d0b5379B2191A4' # need change
account_priv = bytes.fromhex("41EC8616C6EB10C6313DAB6A14589B9E70F762B917AF8DBA7534EA723E95859F") # need change


with open('fairswap_sol_fileSale.abi','r') as f:
    abi = json.load(f)

with open('fairswap_sol_fileSale.bin','r') as f:
    code = f.read()

contract = web3.eth.contract(bytecode=code, abi=abi) 

tx = contract.constructor(account, 10).build_transaction({
    'nonce': web3.eth.get_transaction_count(account),
    'from' : account
    })
signed_tx = web3.eth.account.sign_transaction(tx, account_priv)

tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
#print(tx_hash.hex())

# 通过receipt来获取合约地址

# 可能需要慢一点再get receipt

receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
contract_address = receipt.contractAddress
print(contract_address)

#contract_instance = web3.eth.contract(address="19110fB308358Ff26Ebe09b54be1dC5C39cB0B28", abi = abi)
#stage = contract_instance.functions.printStage().call()
#print("The stage is:",stage)

