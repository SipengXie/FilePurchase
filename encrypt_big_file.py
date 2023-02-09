from file_reader import *
from merkel import Node

def bxor(b1, b2): # use xor for bytes
    result = b""
    for b1, b2 in zip(b1, b2):
        result += bytes([b1 ^ b2])
    return result

array = getWholeFile()
b = []
c = []
key    = b'\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88'
for i in range (len(array)):
    b.append(bxor(Node.hash_int_and_bytes(i, key), array[i]))
    c.append(bxor(b[i],b'1'))

f = open("c_big_file","wb")
for e in b:
    f.write(e)
f.close()

f = open("c_prime_big_file","wb")
for e in c:
    f.write(e)
f.close()