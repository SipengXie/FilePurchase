
import json
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))

account = '0xe5Dc96369d2B1AE7DC82eD5783d0b5379B2191A4' # need change
account_priv = bytes.fromhex("41EC8616C6EB10C6313DAB6A14589B9E70F762B917AF8DBA7534EA723E95859F") # need change

def run(n, length):
    with open('fairswap_sol_fileSale-{n}-{length}.abi'.format(n=n, length=length),'r') as f:
        abi = json.load(f)

    with open('fairswap_sol_fileSale-{n}-{length}.bin'.format(n=n, length=length),'r') as f:
        code = f.read()
    if (abi == None) or (code == None):
        raise Exception("Nothing is read!")

    contract = web3.eth.contract(bytecode=code, abi=abi) 

    tx = contract.constructor(account, 10).build_transaction({
        'nonce': web3.eth.get_transaction_count(account),
        'from' : account
        })

    signed_tx = web3.eth.account.sign_transaction(tx, account_priv)

    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(receipt['gasUsed'])
    contract_address = receipt.contractAddress
    print("{n},{length}:".format(n=n, length=length), contract_address)
    return contract_address
