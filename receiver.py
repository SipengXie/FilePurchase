from web3 import Web3
from typing import List
from merkel import MerkelTree, Node

def bxor(b1, b2): # use xor for bytes
    result = b""
    for b1, b2 in zip(b1, b2):
        result += bytes([b1 ^ b2])
    return result

class Receiver:
    length : int = 1 # 
    n : int #
    key : int #
    ciphertext : List[bytes] #
    plaintext : List[bytes] #
    file : List[bytes] #
    mTree_f : MerkelTree
    mTree_c : MerkelTree

    def __init__(self, ciphertext, n):
        self.ciphertext = ciphertext
        self.mTree_c = MerkelTree(ciphertext)
        self.n = n
    
    def verify_ciphertext(self, cipherRoot):
        return cipherRoot == self.mTree_c.getRootHash()
    
    def accept(self):
        ciphertext_prime = [bxor(i, b'1') for i in self.ciphertext]
        mTree_c_prime = MerkelTree(ciphertext_prime) 
        return mTree_c_prime.getRootHash()  # H(C + 1)

    def decrypt(self, key):
        self.key = key
        self.plaintext = [bxor(Node.hash_2(i,key),self.ciphertext[i]) for i in range(0,len(self.ciphertext))]
        self.file = self.plaintext[:self.n]
        self.mTree_f = MerkelTree(self.file)
    
    def verify_fileRoot(self, fileRoot):
        return self.plaintext[-1] == fileRoot

    def complain_fileRoot(self):
        index = len(self.ciphertext) - 1
        proof = self.mTree_c.get_siblings(index)
        return (self.ciphertext[index], proof)
    
    def complain_file(self, in_1, in_2, out):
        Zin_1 = [self.ciphertext[in_1]]
        Zin_2 = [self.ciphertext[in_2]]
        Zout = self.ciphertext[out]
        proofIn_1 = self.mTree_c.get_siblings(in_1)
        proofIn_2 = self.mTree_c.get_siblings(in_2)
        proofOut = self.mTree_c.get_siblings(out)
        return (Zin_1,Zin_2,Zout,proofIn_1,proofIn_2,proofOut)

    def complain_node(self, in_1, in_2, out):
        Zin_1 = self.ciphertext[in_1]
        Zin_2 = self.ciphertext[in_2]
        Zout = self.ciphertext[out]
        proofIn_1 = self.mTree_c.get_siblings(in_1)
        proofIn_2 = self.mTree_c.get_siblings(in_2)
        proofOut = self.mTree_c.get_siblings(out)
        return (Zin_1,Zin_2,Zout,proofIn_1,proofIn_2,proofOut)

    def search_first_incorrect(self): # [0,n) -> complain_file;[n,len(tree))->complain_node
        #print(self.file)
        my_whole_tree = self.mTree_f.flatten()
        for i in range (0, len(my_whole_tree)):
            if self.plaintext[i] != my_whole_tree[i]:
                return i
        return len(my_whole_tree)

def bytesToHexString(bs):
    return ''.join(['%02X' % b for b in bs])

###
#      G
#    /   \
#   E     F
#  / \   / \
# A   B C   D 
###

if __name__ == "__main__":
    receiver = Receiver([b"\xae\x0f\xb9y\xec\xd8\xd36rX\x1a\x0e\xfe\xc3\xafR'9\xf9\xea\xba\xbc\x19\xd1\xb3eWP\xae*h\x9f",           #A
                         b'\x87\xd2\x10\x0b:]\xeb6\x895\r\xc2G\xa0V{\xb0\xd8kl\x96\x8bD2z\x1b\xe6\x84z\x04\\\x87',                  #B
                         b'\x8e\x97F\x08\x13\xb5\xe3\xec\x9d\xe8\x9ah1_\xd4\xceq>\x94]\xf0\x01\xdcA\x7f`[\x1c\xcb\xa7W\x11',        #C 
                         b"\xa0\x00\x18\xe0\x10\xb3'\x94^.\xc5\xce\x13\x18\xbb\x84\xb3^\x1di\x16\xdb\xf8\x94~{\xce^\xa1B\x14\xa0",  #D 
                         b'p\x83\xa5\x88l\xc7I\x16EW!n\xc3\xb3\xd4\xdb\xd9q\x81\xcbK\x19}\tS\xfb\xd5g\xe5r\xa8\xfc',                #E
                         b'\xc1\xf7\x10-\xf7\xd3\xe4\xb2\xc8\x1f\xcf<\x10\xa2c\x1d\xec\\b\x94\xd0\x1d\xd4\x14PMC\xe1\xc9D\x85s',    #F
                         b'\xfc\x06\x05\xf1\x04(&\x14\xbd\x96\xc4\x1fg \xd6-\xb5[\xefz\xf0\x87k\xee\xd93h\xb1\x0b\x84\x8dI']        #G
    ,4)
    print("AcceptCommit=",bytesToHexString(receiver.accept()))
    #print("H(H(C+1))=",bytesToHexString(Node.hash(receiver.accept())))
    print(receiver.verify_ciphertext(bytearray.fromhex("43E49F77EE2D216AEFB25FE2885B9A6C1A068EB546C2645C97AF2A27AD85255A")))

    E='eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'
    KEY = bytearray.fromhex(E)
    receiver.decrypt(KEY)
    print(receiver.verify_fileRoot(bytearray.fromhex("5F509E99DB6F468DF1F245A28921C8BB3D53F8AA7CED8B2CAB75BDAC76F196A7")))
    print(receiver.search_first_incorrect())

