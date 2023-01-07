from web3 import Web3
from typing import List
from merkel import MerkelTree, Node

def bxor(b1, b2): # use xor for bytes
    result = b""
    for b1, b2 in zip(b1, b2):
        result += bytes([b1 ^ b2])
    return result

class Sender:
    plaintext : List[bytes]
    ciphertext : List[bytes]
    length : int = 1 # each chunk contains how many bytes32, to simplify the test, we set length to 1
    n : int # how many chunks
    key : int # a simple key
    c_prime_commit : bytes # H(H(C + 1))
    mTree_f : MerkelTree
    mTree_c : MerkelTree

    def __init__(self, file: List[bytes], key):
        self.mTree_f = MerkelTree(file)
        self.n = len(file)
        self.key = key

        self.plaintext = self.mTree_f.flatten()

        self.ciphertext = [bxor(Node.hash_2(i,key),self.plaintext[i]) for i in range(0,len(self.plaintext))]
        self.mTree_c = MerkelTree(self.ciphertext)

        ciphertext_prime = [bxor(i, b'1') for i in self.ciphertext]
        mTree_c_prime = MerkelTree(ciphertext_prime) # H(C + 1) = mTree_c_prime.getRootHash()

        self.c_prime_commit = Node.hash(mTree_c_prime.getRootHash()) # H(H(C + 1))

    def deployContract():
        return True
    
    def verifyAcceptCommit(self, acceptCommit):
        return Node.hash(acceptCommit) == self.c_prime_commit

    def revealKey():
        return True


def bytesToHexString(bs):
    return ''.join(['%02X' % b for b in bs])

if __name__ == "__main__" :
    A='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    B='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    C='cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc'
    D='dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd'
    E='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'

    CHUNK1=bytearray.fromhex(A)
    CHUNK2=bytearray.fromhex(B)
    CHUNK3=bytearray.fromhex(C)
    CHUNK4=bytearray.fromhex(D)
    KEY   =bytearray.fromhex(E)

    sender = Sender([CHUNK1,CHUNK2,CHUNK3,CHUNK4], KEY)
    print("ciphertext=",sender.ciphertext)
    print("KEY=",bytesToHexString(KEY))
    print("fileRoot=",bytesToHexString(sender.mTree_f.getRootHash()))
    print("keyCommit=",bytesToHexString(Node.hash(KEY)))
    print("cipherRoot=",bytesToHexString(sender.mTree_c.getRootHash()))
    print("cipherPrimeCommit=",bytesToHexString((sender.c_prime_commit)))