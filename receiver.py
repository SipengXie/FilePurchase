from web3 import Web3
from typing import List
from merkel import MerkelTree, Node
from fileChunk import Chunk

def toBytes(proof):
    for i in range(0, len(proof)):
        if (type(proof[i]) != bytes):
            proof[i] = bytes(proof[i])
    return proof

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
        for i in range (0, self.n):
            chunk_contents : List[bytes] = []
            for j in range (0, self.length):
                shard = bxor(Node.hash_int_and_bytes(i * self.length + j, key), self.encrypted_chunks[i].contents[j])
                chunk_contents.append(shard)

            chunk = Chunk(chunk_contents)
            
            chunks.append(chunk)
        
        # generate plain tree path
        plain_tree_path : List[bytes] = []
        for i in range (0, len(self.encrypted_plain_tree_path)):
            element = bxor(Node.hash_int_and_bytes(self.n * self.length + i, key), self.encrypted_plain_tree_path[i])
            plain_tree_path.append(element)
        
        self.chunks = chunks
        self.plain_tree_path = plain_tree_path

    def decrypt_only_path(self, key):
        plain_tree_path : List[bytes] = []
        for i in range (0, len(self.encrypted_plain_tree_path)):
            element = bxor(Node.hash_int_and_bytes(self.n * self.length + i, key), self.encrypted_plain_tree_path[i])
            plain_tree_path.append(element)
        self.plain_tree_path = plain_tree_path
    
    def verify_fileRoot(self, fileRoot):
        return self.plain_tree_path[-1] == fileRoot

    def complain_about_fileRoot(self):
        input_for_cipher_tree = self.cipher_tree.leaves
        index = len(input_for_cipher_tree) - 1
        proof = self.cipher_tree.get_siblings(index)
        proof = toBytes(proof)
        return input_for_cipher_tree[index].value, proof
    
    def complain_about_chunk(self, in_1: int, in_2: int, out: int):
        # 在合约里Zin_1 Zin_2会被keccack256(abi.encodePacked(·))
        Zin_1 = self.encrypted_chunks[in_1].contents # bytes32[]
        Zin_2 = self.encrypted_chunks[in_2].contents # bytes32[]
        Zout = self.cipher_tree.leaves[out].value # bytes32

        proofIn_1 = self.cipher_tree.get_siblings(in_1) 
        proofIn_2 = self.cipher_tree.get_siblings(in_2)
        proofOut = self.cipher_tree.get_siblings(out)

        proofIn_1 = toBytes(proofIn_1)
        proofIn_2 = toBytes(proofIn_2)
        proofOut = toBytes(proofOut)

        return (Zin_1, Zin_2, Zout, proofIn_1, proofIn_2, proofOut)

    def complain_node(self, in_1 : int, in_2 : int, out : int):
        input_for_cipher_tree = self.cipher_tree.leaves

        Zin_1 = input_for_cipher_tree[in_1].value # bytes32
        Zin_2 = input_for_cipher_tree[in_2].value # bytes32
        Zout = input_for_cipher_tree[out].value  # bytes32

        proofIn_1 = self.cipher_tree.get_siblings(in_1)
        proofIn_2 = self.cipher_tree.get_siblings(in_2)
        proofOut = self.cipher_tree.get_siblings(out)

        proofIn_1 = toBytes(proofIn_1)
        proofIn_2 = toBytes(proofIn_2)
        proofOut = toBytes(proofOut)

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

if __name__ == "__main__":
    # TODO: Add test
    #print("1")
    contentReceived_0 = [bytes.fromhex('75d7e4b7ec8defc4effb61d1d79a264119687ac721a7fe359af06d444ceaacee'), 
                         bytes.fromhex('ff0322683be7f952abcf5017278541321e2d09c5acfd6d1d9f08f8dcd385a121')]
    contentReceived_1 = [bytes.fromhex('b95483ecc4a911024479b5262da79884eda2098e0b21269ac3d274c66dc093fc'),
                         bytes.fromhex('df71e3d821d03dc5c499337456d3d39853daa57a0891933027b1acf3c332ba50')]
    contentReceived_2 = [bytes.fromhex('2f2f53a9eaaea0d3b9c41ef0338972de31f107457e2348cd34c8818c91d94e25'), 
                         bytes.fromhex('b6a70786facf847075bb5080a876a11648806fdc2d7fc844346005dcf99c01df')]
    contentReceived_3 = [bytes.fromhex('60110c6dfeabc37ed0fb9a7adcb55bfe3aec5dfb5e0fdba8bf03d824a5147da5'), 
                         bytes.fromhex('969995a6a1eb7aef0691211ec544df758738882f73e059b027741e3435114ad1')]
    
    chunksReceived = [Chunk(contentReceived_0), Chunk(contentReceived_1), Chunk(contentReceived_2), Chunk(contentReceived_3)]
    pathReceived =  [bytes.fromhex('0e0047f3afb37c013a6fa6e00051ac0d6581c9266bcf0bd8bd7b234907557ef0'), 
                     bytes.fromhex('57ff7558523358c98036a3cd28ea71a3088f9f4a86852075305720aca2e3ad5e'), 
                     bytes.fromhex('7e1f57ca2c5ef11bc537f39bbbb91ede58e324c32054d6fac50eb8bf8bc487ca')]

    h_C_received = bytes.fromhex('3bcf26d41c5323147ed44cff30096643857e19d9c53e26badc388e11e2655735') # which is cipher root
    H_H_C_plus_one_received = bytes.fromhex('a5c397b3fe4a364897fee5517a88472460d67240d8a43963a528970cad8cb0a0')

    receiver = Receiver(4, 2)

    receiver.receive_cipherText(chunksReceived, pathReceived)
    receiver.verify_ciphertext(h_C_received)
    H_C_plus_one = receiver.accept()

    print("receiver's H(C+1):", H_C_plus_one.hex())

    print("receiver's H(H(C+1)):",Node.hash_bytes(H_C_plus_one).hex())
    print("sender's H(H(C+1)):", H_H_C_plus_one_received.hex())

    key    = b'\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88'
    receiver.decrypt(key=key)

    fileRoot = bytes.fromhex('8c1065b93751029e31b69574b5e3c2a9d2d7301d4dff760b3ef38da29e06d481')
    print(receiver.verify_fileRoot(fileRoot))

    print("testing complain about fileRoot")
    Zm, Proof = receiver.complain_about_fileRoot()
    print("Zm:", Zm)
    print("Proof:", Proof)
    print("Verify:", receiver.cipher_tree.verify(6, Zm, Proof, h_C_received))

    print("testing complain about chunk")
    Zin_1, Zin_2, Zout, proofIn_1, proofIn_2, proofOut = receiver.complain_about_chunk(in_1=0, in_2=1, out=4)
    print("Zin_1:", Zin_1)
    print("Zin_2:", Zin_2)
    print("Zout:", Zout)
    print("proofOut=", proofOut)
    print("proofIn_1=",proofIn_1)
    print("Verify Zin_1:", receiver.cipher_tree.verify(0, Node.hash_bytes(Zin_1[0]+Zin_1[1]), proofIn_1, h_C_received))
    print("Verify Zin_2:", receiver.cipher_tree.verify(1, Node.hash_bytes(Zin_2[0]+Zin_2[1]), proofIn_2, h_C_received))
    print("Verify Zout:", receiver.cipher_tree.verify(4, Zout, proofOut, h_C_received))
    
    print("testing complain about node")
    Zin_1, Zin_2, Zout, proofIn_1, proofIn_2, proofOut = receiver.complain_node(in_1 = 4, in_2 = 5, out = 6)
    print("Zin_1:", Zin_1)
    print("Zin_2:", Zin_2)
    print("Zout:", Zout)
    print("proofOut=", proofOut)
    print("proofIn=", proofIn_1)
    print("Verify Zin_1:", receiver.cipher_tree.verify(4, Zin_1, proofIn_1, h_C_received))
    print("Verify Zin_2:", receiver.cipher_tree.verify(5, Zin_2, proofIn_2, h_C_received))
    print("Verify Zout:", receiver.cipher_tree.verify(6, Zout, proofOut, h_C_received))