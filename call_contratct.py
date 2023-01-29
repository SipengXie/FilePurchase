import json
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
# dev0

account = '0xe5Dc96369d2B1AE7DC82eD5783d0b5379B2191A4' # need change
account_priv = bytes.fromhex("41EC8616C6EB10C6313DAB6A14589B9E70F762B917AF8DBA7534EA723E95859F") # need change


with open('fairswap_sol_fileSale.abi','r') as f:
    abi = json.load(f)


contract_address = "0x2B37F2cbD717455805B7e80488010306e7Ec24be"

contract = web3.eth.contract(address=contract_address, abi = abi)
# nonce = web3.eth.get_transaction_count(account)

# watch stage
stage = contract.functions.printStage().call()
print("The stage is:",stage)

# accept
H_C_plus_one = "1f288d0fa2ad72dc13e3465e2ca345d52fecfb89f2aa0cb69ec0b2ef225cfa5c"
tx = contract.functions.accept(bytes.fromhex(H_C_plus_one)).build_transaction({
    'nonce': web3.eth.get_transaction_count(account),
    'value':10,
    'from':account})
#print(tx)
#print(contract.functions.accept(bytes.fromhex(H_C_plus_one)).estimate_gas())
signed_tx = web3.eth.account.sign_transaction(tx, account_priv)
tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
print(receipt)

stage = contract.functions.printStage().call()
print("The stage is:",stage)