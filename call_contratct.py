import json
from web3 import Web3

web3 = Web3(Web3.HTTPProvider("http://localhost:8545"))
# dev0

account = '0xe5Dc96369d2B1AE7DC82eD5783d0b5379B2191A4' # need change
account_priv = bytes.fromhex("41EC8616C6EB10C6313DAB6A14589B9E70F762B917AF8DBA7534EA723E95859F") # need change


with open('fairswap_sol_fileSale.abi','r') as f:
    abi = json.load(f)


contract_address = "0x58296e02d7071a1E8957DB8853f1eC4aE22dED1B"

contract = web3.eth.contract(address=contract_address, abi = abi)

# watch stage
def getStage():
    stage = contract.functions.printStage().call()
    print("The stage is:",stage)

# accept
def accept():
    getStage()
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
    getStage()

# key reveal
def keyReveal():
    getStage()
    key    = b'\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88'
    #print(contract.functions.revealKey(key).estimate_gas())
    tx = contract.functions.revealKey(key).build_transaction({
        'nonce' : web3.eth.get_transaction_count(account),
        'from'  : account
    })
    #print(tx)
    signed_tx = web3.eth.account.sign_transaction(tx, account_priv)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(receipt)
    getStage()

# watch stage
#stage = contract.functions.printStage().call()
#print("The stage is:",stage)

# complain about fileRoot
def complainFileRoot():
    getStage()
    Zm = b'~\x1fW\xca,^\xf1\x1b\xc57\xf3\x9b\xbb\xb9\x1e\xdeX\xe3$\xc3 T\xd6\xfa\xc5\x0e\xb8\xbf\x8b\xc4\x87\xca'
    Proof = [b'~\x1fW\xca,^\xf1\x1b\xc57\xf3\x9b\xbb\xb9\x1e\xdeX\xe3$\xc3 T\xd6\xfa\xc5\x0e\xb8\xbf\x8b\xc4\x87\xca', b'kd@G~\xe5\xd8\x91\x1f\x04\x90\x95\xb58\xce\xfe\x0c\xf6\xd7\xf45A-\x07\xbc\xea\xbaB\xcf\x9a\x11\xb9', b"'\xf5\x17\x8a\xa2R\xfb\xc52\xe0\xd3\x16\x8fF{\xc8$NS&zD>K\xc9(\xd4\x01\xea\x92\xf6p"]
    tx = contract.functions.complainAboutRoot(Zm, Proof).build_transaction({
        'nonce' : web3.eth.get_transaction_count(account),
        'from'  : account
    })
    print(tx)
    signed_tx = web3.eth.account.sign_transaction(tx, account_priv)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(receipt)
    logs = contract.events.ComplainFailed().processReceipt(receipt)
    print(logs)
    getStage()

def complainChunk():
    getStage()
    indexOut = 4
    indexIn = 0
    Zin_1 = [b'u\xd7\xe4\xb7\xec\x8d\xef\xc4\xef\xfba\xd1\xd7\x9a&A\x19hz\xc7!\xa7\xfe5\x9a\xf0mDL\xea\xac\xee', 
             b'\xff\x03"h;\xe7\xf9R\xab\xcfP\x17\'\x85A2\x1e-\t\xc5\xac\xfdm\x1d\x9f\x08\xf8\xdc\xd3\x85\xa1!']
    Zin_2 = [b'\xb9T\x83\xec\xc4\xa9\x11\x02Dy\xb5&-\xa7\x98\x84\xed\xa2\t\x8e\x0b!&\x9a\xc3\xd2t\xc6m\xc0\x93\xfc', 
             b"\xdfq\xe3\xd8!\xd0=\xc5\xc4\x993tV\xd3\xd3\x98S\xda\xa5z\x08\x91\x930'\xb1\xac\xf3\xc32\xbaP"]

    Zout = b'\x0e\x00G\xf3\xaf\xb3|\x01:o\xa6\xe0\x00Q\xac\re\x81\xc9&k\xcf\x0b\xd8\xbd{#I\x07U~\xf0'

    proofIn_1 = [b'0\xb7\x86\xb9\xc22\xcb\x9b4\xd6\x83\xe6C0\x17o,\xa3\xed1\xe8M\xf8*\xaf\xdc\xb6A\x1c\\AC', 
                 b'rp\x8a\xac0\x02\xa1\x9f\xc5\x9f\xf0\x84\xc0\n\xad\x08-\xf9\xb8V.U\x91)]\xcd\xe2\x05c+>a', 
                 b'\x0b\xc2\x95\xaa\x04\x7f\xee~gZ\xd0<\xaa\xa4\xdad\x88\xb2\xcd\xe7!\x1c5\x05Kr\xf3O;\xb03%']

    proofOut= [b'W\xffuXR3X\xc9\x806\xa3\xcd(\xeaq\xa3\x08\x8f\x9fJ\x86\x85 u0W \xac\xa2\xe3\xad^', 
               b'\xca\x91/\xc2\x01\x02*\x1f\x18M\x81\xed\x85h\xb9\x87\xf3\x00\x06\xaa\xbe\xcb\xa8i\xe4V\x9fR\xfe\xdf\xa7W',
               b"'\xf5\x17\x8a\xa2R\xfb\xc52\xe0\xd3\x16\x8fF{\xc8$NS&zD>K\xc9(\xd4\x01\xea\x92\xf6p"]

    tx = contract.functions.complainAboutLeaf(indexOut, indexIn, Zout, Zin_1, Zin_2, proofOut, proofIn_1).build_transaction({
        'nonce' : web3.eth.get_transaction_count(account),
        'from'  : account
    })
    print(tx)
    signed_tx = web3.eth.account.sign_transaction(tx, account_priv)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(receipt)
    logs = contract.events.ComplainFailed().processReceipt(receipt)
    print(logs)
    getStage()

def complainNode():
    getStage()
    indexOut = 6
    indexIn = 4
    Zout = b'~\x1fW\xca,^\xf1\x1b\xc57\xf3\x9b\xbb\xb9\x1e\xdeX\xe3$\xc3 T\xd6\xfa\xc5\x0e\xb8\xbf\x8b\xc4\x87\xca'
    Zin_1 = b'\x0e\x00G\xf3\xaf\xb3|\x01:o\xa6\xe0\x00Q\xac\re\x81\xc9&k\xcf\x0b\xd8\xbd{#I\x07U~\xf0'
    Zin_2 = b'W\xffuXR3X\xc9\x806\xa3\xcd(\xeaq\xa3\x08\x8f\x9fJ\x86\x85 u0W \xac\xa2\xe3\xad^'
    proofOut= [b'~\x1fW\xca,^\xf1\x1b\xc57\xf3\x9b\xbb\xb9\x1e\xdeX\xe3$\xc3 T\xd6\xfa\xc5\x0e\xb8\xbf\x8b\xc4\x87\xca',
               b'kd@G~\xe5\xd8\x91\x1f\x04\x90\x95\xb58\xce\xfe\x0c\xf6\xd7\xf45A-\x07\xbc\xea\xbaB\xcf\x9a\x11\xb9',
               b"'\xf5\x17\x8a\xa2R\xfb\xc52\xe0\xd3\x16\x8fF{\xc8$NS&zD>K\xc9(\xd4\x01\xea\x92\xf6p"]
    proofIn= [b'W\xffuXR3X\xc9\x806\xa3\xcd(\xeaq\xa3\x08\x8f\x9fJ\x86\x85 u0W \xac\xa2\xe3\xad^', 
              b'\xca\x91/\xc2\x01\x02*\x1f\x18M\x81\xed\x85h\xb9\x87\xf3\x00\x06\xaa\xbe\xcb\xa8i\xe4V\x9fR\xfe\xdf\xa7W',
              b"'\xf5\x17\x8a\xa2R\xfb\xc52\xe0\xd3\x16\x8fF{\xc8$NS&zD>K\xc9(\xd4\x01\xea\x92\xf6p"]
    tx = contract.functions.complainAboutNode(indexOut, indexIn, Zout, Zin_1, Zin_2, proofOut, proofIn).build_transaction({
        'nonce' : web3.eth.get_transaction_count(account),
        'from'  : account
    })
    print(tx)
    signed_tx = web3.eth.account.sign_transaction(tx, account_priv)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(receipt)
    logs = contract.events.ComplainFailed().processReceipt(receipt)
    print(logs)
    getStage()

def noComplain():
    getStage()
    tx = contract.functions.noComplain().build_transaction({
        'nonce' : web3.eth.get_transaction_count(account),
        'from'  : account
    })
    print(tx)
    signed_tx = web3.eth.account.sign_transaction(tx, account_priv)
    tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
    print(receipt)
    try:
        getStage()
    except:
        print("成功销毁合约!")

if __name__ == "__main__":
    #accept()
    #keyReveal()
    #complainFileRoot()
    #complainChunk()
    #complainNode()
    noComplain()