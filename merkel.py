from typing import List
from web3 import Web3
from math import log2, floor


class Node:
    def __init__(self, left, right, value)-> None:
        self.left: Node = left
        self.right: Node = right
        self.value = value
        self.parent : Node = None
    
    @staticmethod
    def hash_bytes(val: bytes) -> bytes:
        return Web3.solidityKeccak(["bytes32"],[val])
    
    def hash_int_and_bytes(val_1:int, val_2:bytes) -> bytes:
        return bytes(Web3.solidityKeccak(["uint256","bytes32"],[val_1,val_2]))

    def __str__(self):
        return(str(self.value))

"""
The MerkelTree must be initialized with bytes32[]
"""

class MerkelTree:

    root : Node = None
    leaves : List[Node] = None
    n : int = 0
    depth : int = 0

    def __init__(self, leaves) -> None:
        self.leaves : List[Node] = [Node(None, None, e) for e in leaves]
        self.root = self.__buildTreeRec(self.leaves)
        self.n = len(self.leaves)
        self.depth = floor(log2(self.n))


    def __buildTreeRec(self, nodes : List[Node]) -> Node:
        if len(nodes) == 1:
            return nodes[0]

        if (len(nodes) % 2 == 1) :
            nodes.append(nodes[-1]) 

        half : int = len(nodes) >> 1
        
        left : Node = self.__buildTreeRec(nodes[:half])
        right : Node = self.__buildTreeRec(nodes[half:])
        value : bytes = Node.hash_bytes(left.value + right.value) # left right是明文树叶子的时候 是两边的rawContents的连接
                                                                  # left right是密文树叶子的时候 是两边的直接的值的连接
                                                                  # left right不是叶子的时候 是两边直接的值的连接

        cur_node = Node(left, right, value)
        left.parent = cur_node
        right.parent = cur_node

        return cur_node

    def getRootHash(self)-> bytes:
         return self.root.value

    def get_siblings(self, index) -> List[bytes]:               # 只会对密文树使用这个函数
        ret = []
        if (index < 0 or index >= self.n):
            return ret
        parent = self.leaves[index].parent

        for i in range (0, self.depth):
            if ( ((index & (1 << i)) >> i) & 1): # current node is right
                ret.append(parent.left.value)
            else:                                # current node is left
                ret.append(parent.right.value)
            parent = parent.parent
        return ret
        
    def verify(self, index, leave_hash, siblings: List[bytes], root_hash) -> bool: # 只会对密文树使用这个函数
        if (index < 0 or index >= self.n):
            return False
        if (len(siblings) != self.depth):
            return False
        cur_hash = leave_hash

        for i in range (0, self.depth):
            if ( ((index & (1 << i)) >> i) & 1): # current node is right
                cur_hash = Node.hash_bytes(siblings[i] + cur_hash)
            else:                                # current node is left
                cur_hash = Node.hash_bytes(cur_hash + siblings[i])
        return cur_hash == root_hash

    def flatten(self): # flat the tree without giving leaves in return; only returns path
        nodes = self.leaves
        ret = []
        nodes_length = len(nodes)
        while (nodes_length > 1):
            temp_nodes = []
            temp_ret = []
            for i in range (0, nodes_length, 2):
                temp_nodes.append(nodes[i].parent)
                temp_ret.append(nodes[i].parent.value)
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
    print(0)
    # TODO: add test