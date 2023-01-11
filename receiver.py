from web3 import Web3
from typing import List
from merkel import MerkelTree, Node
from fileChunk import Chunk
def bxor(b1, b2): # use xor for bytes
    result = b""
    for b1, b2 in zip(b1, b2):
        result += bytes([b1 ^ b2])
    return result

class Receiver:
    length : int = 1 # 
    n : int #
    key : int #
    encrypted_chunks : List[Chunk]
    encrypted_plain_tree_path : List[bytes]
    cipher_tree : MerkelTree

    chunks : List[Chunk]
    plain_tree_path : List[bytes]
    
    def __init__(self, n, length):
        self.n = n
        self.length = length

    def receive_cipherText(self, encrypted_chunks : List[Chunk], encrypted_plain_tree_path : List[bytes]):
        self.encrypted_chunks = encrypted_chunks
        self.encrypted_plain_tree_path = encrypted_plain_tree_path

        input_for_cipher_tree : List[bytes] = [chunk.get_hash() for chunk in encrypted_chunks] + encrypted_plain_tree_path
        self.cipher_tree = MerkelTree(input_for_cipher_tree)
    
    def verify_ciphertext(self, cipherRoot):
        return cipherRoot == self.cipher_tree.getRootHash()
    
    def accept(self):

        encrypted_chunks_prime = [chunk.xor_one() for chunk in self.encrypted_chunks]
        encrypted_plain_tree_path_prime = [bxor(element,b'1') for element in self.encrypted_plain_tree_path]

        input_for_cipher_tree_prime : List[bytes] = [chunk.get_hash() for chunk in encrypted_chunks_prime] + encrypted_plain_tree_path_prime

        cipher_tree_prime = MerkelTree(input_for_cipher_tree_prime)

        return cipher_tree_prime.getRootHash()  # H(C + 1)

    def decrypt(self, key):
        self.key = key

        # generate plain text : chunks
        chunks : List[Chunk] = []
        for i in range (self.n):
            chunk_contents : List[bytes] = []
            for j in range (self.length):
                shard = bxor(Node.hash_int_and_bytes(i * self.length + j, key), self.encrypted_chunks[i].contents[j])
                chunk_contents.append(shard)

            chunk = Chunk(chunk_contents)
            
            chunks.append(chunk)
        
        # generate plain tree path
        plain_tree_path : List[bytes] = []
        for i in range (len(self.encrypted_plain_tree_path)):
            element = bxor(Node.hash_int_and_bytes(self.n * self.length + i, key), self.encrypted_plain_tree_path[i])
            plain_tree_path.append(element)
        
        self.chunks = chunks
        self.plain_tree_path = plain_tree_path
    
    def verify_fileRoot(self, fileRoot):
        return self.plain_tree_path[-1] == fileRoot

    def complain_about_fileRoot(self):
        input_for_cipher_tree = self.cipher_tree.leaves
        index = len(input_for_cipher_tree) - 1
        proof = self.cipher_tree.get_siblings(index)
        return (input_for_cipher_tree[index], proof)
    
    def complain_about_chunk(self, in_1, in_2, out):
        Zin_1 = self.encrypted_chunks[in_1].contents # bytes32[]
        Zin_2 = self.encrypted_chunks[in_2].contents # bytes32[]
        Zout = self.cipher_tree.leaves[out] # bytes32

        proofIn_1 = self.cipher_tree.get_siblings(in_1) # 在合约里Zin_1 Zin_2会被keccack256(abi.encodePacked(·))
        proofIn_2 = self.cipher_tree.get_siblings(in_2)
        proofOut = self.cipher_tree.get_siblings(out)

        return (Zin_1,Zin_2,Zout,proofIn_1,proofIn_2,proofOut)

    def complain_node(self, in_1, in_2, out):
        input_for_cipher_tree = self.cipher_tree.leaves

        Zin_1 = input_for_cipher_tree[in_1]
        Zin_2 = input_for_cipher_tree[in_2]
        Zout = input_for_cipher_tree[out]

        proofIn_1 = self.cipher_tree.get_siblings(in_1)
        proofIn_2 = self.cipher_tree.get_siblings(in_2)
        proofOut = self.cipher_tree.get_siblings(out)

        return (Zin_1,Zin_2,Zout,proofIn_1,proofIn_2,proofOut)

    def search_first_incorrect(self): # [0,n) -> complain_file;[n,len(tree))->complain_node

        # first we check the path
        plain_tree = MerkelTree(self.chunks)
        my_path = plain_tree.flatten()
        if len (my_path) != len(self.plain_tree_path):
            raise Exception("Unmatched path length! my_path:" + len(my_path) + " expected" + len(self.plain_tree_path))
        for i in range (0, len(my_path)):
            if self.plain_tree_path[i] != my_path[i]:
                return i

        return len(my_path)

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
    # TODO: Add test
    print("1")
