from typing import List
from web3 import Web3
from math import log2, floor
class Node:
    def __init__(self, left, right, value: bytes)-> None:
        self.left: Node = left
        self.right: Node = right
        self.hash_value = value
        self.parent : Node = None
    
    @staticmethod
    def hash(val: bytes)-> bytes:
        return Web3.solidityKeccak(["bytes32"],[val])
    
    def hash_2(val_1:int, val_2:bytes) -> bytes:
        return bytes(Web3.solidityKeccak(["uint256","bytes32"],[val_1,val_2]))

    def __str__(self):
        return(str(self.hash_value))

"""
The MerkelTree must be initialized with bytes32[]
"""

class MerkelTree:

    root : Node = None
    leaves : List[Node] = None
    n : int = 0
    depth : int = 0

    def __init__(self, bytes32 : List[bytes]) -> None:
        self.leaves : List[Node] = [Node(None, None, e) for e in bytes32]
        self.root = self.__buildTreeRec(self.leaves)
        self.n= len(self.leaves)
        self.depth = floor(log2(self.n))

    def __buildTreeRec(self, nodes : List[Node]) -> Node:
        if len(nodes) == 1:
            return nodes[0]

        if (len(nodes) % 2 == 1) :
            nodes.append(nodes[-1]) 
        half : int = len(nodes) // 2
        
        left : Node = self.__buildTreeRec(nodes[:half])
        right : Node = self.__buildTreeRec(nodes[half:])
        hash_value : bytes = Node.hash(left.hash_value + right.hash_value)

        cur_node = Node(left, right, hash_value)
        left.parent = cur_node
        right.parent = cur_node

        return cur_node

    def getRootHash(self)-> bytes:
         return self.root.hash_value

    def get_siblings(self, index) -> List[bytes]:
        ret = []
        if (index < 0 or index >= self.n):
            return ret
        parent = self.leaves[index].parent

        for i in range (0, self.depth):
            if ( ((index & (1 << i)) >> i) & 1): # current node is right
                ret.append(parent.left.hash_value)
            else:                                # current node is left
                ret.append(parent.right.hash_value)
            parent = parent.parent
        return ret
        
    def verify(self, index, leave_hash, siblings: List[bytes], root_hash) -> bool:
        if (index < 0 or index >= self.n):
            return False
        if (len(siblings) != self.depth):
            return False
        cur_hash = leave_hash

        for i in range (0, self.depth):
            if ( ((index & (1 << i)) >> i) & 1): # current node is right
                cur_hash = Node.hash(siblings[i] + cur_hash)
            else:                                # current node is left
                cur_hash = Node.hash(cur_hash + siblings[i])
        return cur_hash == root_hash

    def flatten(self): # flat the tree
        nodes = self.leaves
        ret = [[item.hash_value for item in nodes]]
        nodes_length = len(nodes)
        while (nodes_length > 1):
            temp_nodes = []
            temp_ret = []
            for i in range (0, nodes_length, 2):
                temp_nodes.append(nodes[i].parent)
                temp_ret.append(nodes[i].parent.hash_value)
            ret.append(temp_ret)
            nodes = temp_nodes
            nodes_length = len(nodes)
        return [i for item in ret for i in item]

    """
    对应index个的上一层开始、这一层开始以及下一层开始
    """
    def get_three_start(self, index):
        last_st=cur_st=nxt_st=0
        cur_node_num=self.n
        while (cur_node_num > 1):
            if (cur_node_num & 1):
                cur_node_num += 1
            nxt_st = cur_st + cur_node_num
            if (index >= cur_st and index < nxt_st):
                return (last_st, cur_st, nxt_st)
            last_st = cur_st
            cur_st = nxt_st
            cur_node_num >>= 1
        return None


def bytesToHexString(bs):
    return ''.join(['%02X ' % b for b in bs])

if __name__ == "__main__":
    mTree = MerkelTree([b'0',b'1',b'2',b'3',b'4',b'5',b'6'])
    print("The root is:",mTree.getRootHash())

    path = mTree.get_siblings(4)
    print("The Path is:",path)

    print(mTree.verify(4, b'4', path, mTree.getRootHash()))


    # 用solidity测一下
    #A='aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
    #B='bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb'
    #CHUNK1=bytearray.fromhex(A)
    #CHUNK2=bytearray.fromhex(B)
    #print(CHUNK1)
    #print(CHUNK2)
    #print(bytesToHexString(Node.hash(CHUNK1+CHUNK2)))
    #print(bytesToHexString(Node.hash(CHUNK1)))

    #print(bytesToHexString(Node.hash(CHUNK2+CHUNK1)))
    #print(bytesToHexString(Node.hash(CHUNK2)))

    #print(bytesToHexString(Node.hash_2(1,CHUNK1)))