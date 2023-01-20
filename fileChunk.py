from merkel import Node
from typing import List
def bxor(b1, b2): # use xor for bytes
    result = b""
    for b1, b2 in zip(b1, b2):
        result += bytes([b1 ^ b2])
    return result

class Chunk:
    length : int
    contents : List[bytes]
    rawContents : bytes

    def __init__(self, contents: List[bytes]) :
        self.length = len(contents)
        self.contents = contents
        self.rawContents = b''.join(contents)
  
    def get_hash(self):
        return Node.hash_bytes(self.rawContents)

    def __add__(self, another):
        return self.rawContents + another.rawContents

    def calc_rawContents(self):
        self.rawContents = ''.join(self.contents)
    
    def xor_one(self):
        contents = []
        for i in range (self.length):
            contents.append(bxor(self.contents[i], b'1'))
        return Chunk(contents)
    
