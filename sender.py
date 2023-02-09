import time
from typing import List
from merkel import MerkelTree, Node
from fileChunk import Chunk

def bxor(b1, b2): # use xor for bytes
    result = b""
    for b1, b2 in zip(b1, b2):
        result += bytes([b1 ^ b2])
    return result

class Sender:

    length : int # each chunk contains how many bytes32
    n : int # how many chunks
    key : bytes # a simple 32bytes long key

    def __init__(self, n : int, chunkLength : int, key : bytes):
        self.length = chunkLength
        self.n = n
        self.key = key

    # cannot be used in big file encryption!
    def Encryption(self, chunks: List[Chunk]):

        # do encryption for plaintext;
        # meanwhile generate C+1=cipher prime
        encrypted_chunks : List[Chunk] = [] # cipher
        encrypted_chunks_prime : List[Chunk] = [] # cipher prime
        for i in range (0, self.n):
            print("Encrypting No.{n} Chunk".format(n = i))
            encrypted_chunk_contents : List[bytes] = []

            for j in range (self.length):
                shard = bxor(Node.hash_int_and_bytes(i * self.length + j, self.key), chunks[i].contents[j])
                encrypted_chunk_contents.append(shard)    

            encrypted_chunk = Chunk(encrypted_chunk_contents)

            encrypted_chunk_prime = encrypted_chunk.xor_one()

            encrypted_chunks.append(encrypted_chunk)
            encrypted_chunks_prime.append(encrypted_chunk_prime) # each chunk contains 2 contents, each content contains 1 byte


        print("encrypted_chunks_prime=")
        for chunk in encrypted_chunks_prime:
            print(chunk.contents)
        # generate plain tree
        print("Making Plain Tree")
        st = time.time()
        mTree_plain = MerkelTree(chunks)
        plain_tree_path = mTree_plain.flatten()

        # do encryption for plain tree path;
        encrypted_plain_tree_path : List[bytes] = []
        encrypted_plain_tree_path_prime : List[bytes] = []

        for i in range (0, len(plain_tree_path)):
            encrypted_element = bxor(Node.hash_int_and_bytes(self.n * self.length + i, self.key), plain_tree_path[i])
            encrypted_plain_tree_path.append(encrypted_element)
            encrypted_plain_tree_path_prime.append(bxor(encrypted_element,b'1'))

        # generate cipher tree
        input_for_cipher_tree : List[bytes] = [chunk.get_hash() for chunk in encrypted_chunks] + encrypted_plain_tree_path

        # generate cipher prime tree
        input_for_cipher_tree_prime : List[bytes] = [chunk.get_hash() for chunk in encrypted_chunks_prime] + encrypted_plain_tree_path_prime

        mTree_cipher = MerkelTree(input_for_cipher_tree)
        mTree_cipher_prime = MerkelTree(input_for_cipher_tree_prime)

        # the real cipher text that will be transferred
        # or we can do this: 
        # cipherText = encrypted_chunks + encrypted_plain_tree_path
        # cipherText = [element.rawContents for element in encrypted_chunks] + encrypted_plain_tree_path
        cipher_commit = mTree_cipher.getRootHash() # we consider this to be H(C)
        cipher_commit_prime = mTree_cipher_prime.getRootHash() # we consider this to be H(C+1)
        ed = time.time()
        # return fileRoot, {Echunks + Epath} = C, H(C), H(H(C+1))
        print("Encoding Time =",ed-st)
        return plain_tree_path[-1], encrypted_chunks, encrypted_plain_tree_path, cipher_commit, Node.hash_bytes(cipher_commit_prime)
  
    # accepteCommmit = H(C+1), cipher_commit_prime should be H(H(C+1)) note this is different from the Encryption() method
    def verifyAcceptCommit(self, acceptCommit, cipher_commit_prime): 
        return Node.hash_bytes(acceptCommit) == cipher_commit_prime

    # work with encrypted file, provided chunklized cipher and cipher prime
    def workWithEncryptedFile(self, plain_chunks : List[Chunk], encrypted_chunks : List[Chunk], encrypted_chunks_prime : List[Chunk]):
        print("Making Plain Tree")
        time_counter = 0 # tree building
        func_st = time.time() # func time
        mTree_plain = MerkelTree(plain_chunks)
        time_counter += time.time()-func_st
        plain_tree_path = mTree_plain.flatten()

        encrypted_tree_path : List[bytes] = []
        encrypted_tree_path_prime : List[bytes] = []
        
        for i in range (0, len(plain_tree_path)):
            encrypted_element = bxor(Node.hash_int_and_bytes(self.n * self.length + i, self.key), plain_tree_path[i])
            encrypted_tree_path.append(encrypted_element)
            encrypted_tree_path_prime.append(bxor(encrypted_element,b'1'))

        # generate cipher tree
        input_for_cipher_tree : List[bytes] = [chunk.get_hash() for chunk in encrypted_chunks] + encrypted_tree_path

        # generate cipher prime tree
        input_for_cipher_tree_prime : List[bytes] = [chunk.get_hash() for chunk in encrypted_chunks_prime] + encrypted_tree_path_prime

        st = time.time()
        mTree_cipher = MerkelTree(input_for_cipher_tree)
        mTree_cipher_prime = MerkelTree(input_for_cipher_tree_prime)
        time_counter += time.time() - st

        # the real cipher text that will be transferred
        # or we can do this: 
        # cipherText = encrypted_chunks + encrypted_plain_tree_path
        # cipherText = [element.rawContents for element in encrypted_chunks] + encrypted_plain_tree_path
        cipher_commit = mTree_cipher.getRootHash() # we consider this to be H(C)
        cipher_commit_prime = mTree_cipher_prime.getRootHash() # we consider this to be H(C+1)
        func_ed = time.time()
        # return fileRoot, {Echunks + Epath} = C, H(C), H(H(C+1)), H(C+1)
        print("Function running time =", func_ed-func_st)
        print("Tree Building Time =",time_counter)
        return plain_tree_path[-1], encrypted_tree_path, cipher_commit, Node.hash_bytes(cipher_commit_prime), cipher_commit_prime


def bytesToHexString(bs):
    return ''.join(['%02X' % b for b in bs])

if __name__ == "__main__" :
#   print(0)
    file_0 = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    file_1 = b'\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11\x11'
    file_2 = b'\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22\x22'
    file_3 = b'\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33\x33'
    file_4 = b'\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44\x44'
    file_5 = b'\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55\x55'
    file_6 = b'\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66\x66'
    file_7 = b'\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77\x77'
    key    = b'\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88'
    chunk_1 = Chunk([file_0, file_1])
    chunk_2 = Chunk([file_2, file_3])
    chunk_3 = Chunk([file_4, file_5])
    chunk_4 = Chunk([file_6, file_7])

    test_sender = Sender(4, 2, key)
    fileRoot, cipherChunks, cipherPath, h_C, H_H_C_plus_one = test_sender.Encryption([chunk_1, chunk_2, chunk_3, chunk_4])
    
    print("fileRoot=",fileRoot.hex())
    print("keyCommit=",Node.hash_bytes(key).hex())

    print("CipherChunks:")
    for i in range(0,len(cipherChunks)):
        contents = cipherChunks[i].contents
        for j in range(0, len(contents)):
            contents[j] = contents[j].hex()
        print(contents)

    for i in range (0, len(cipherPath)):
        cipherPath[i] = cipherPath[i].hex()
    print("CipherPath = ", cipherPath)
    print("H(C) = ", h_C.hex())
    print("H(H(C+1)) = ", H_H_C_plus_one.hex())