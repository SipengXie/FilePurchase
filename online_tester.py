import json
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

# dev0
account = '0xE5DC96369D2B1AE7DC82ED5783D0B5379B2191A4' # need change
account_priv = bytes.fromhex("41EC8616C6EB10C6313DAB6A14589B9E70F762B917AF8DBA7534EA723E95859F") # neec change


with open('fairswap_sol_fileSale.abi','r') as f:
    abi = json.load(f)

with open('fairswap_sol_fileSale.bin','r') as f:
    code = f.read()

contract = web3.eth.contract(bytecode=code, abi=abi) 
# pdb.set_trace()
nonce = web3.eth.get_transaction_count(account)

tx = contract.constructor(account, 10).build_transaction({'nonce':nonce})
signed_tx = web3.eth.account.sign_transaction(tx, account_priv)

tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
print(tx_hash)
# 通过receipt来获取合约地址

address = web3.eth.get_transaction_receipt(tx_hash)['contractAddress']
print(address)