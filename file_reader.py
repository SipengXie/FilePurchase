import os
from fileChunk import Chunk

def chunklize(fileName: str, chunkLength, contentLength):
    # chunkLength means the length of contents
    # should be 1 2 4 8 16 32 64 128 512 1024 2048 times 32bytes
    # contentLength means the length of each content
    # for big_file and c_big_file = 32, for c_prime_big_file = 1
    f = open(fileName,"rb")
    f.seek(0, os.SEEK_END)
    length = f.tell()
    f.close()

    array = []
    chunkList = []
    f = open(fileName,"rb")
    for _ in range (0, length, contentLength):
        array.append(f.read(contentLength))
    f.close()

    for i in range (0, len(array), chunkLength):
        chunkList.append(Chunk(array[i:i+chunkLength]))
    return chunkList
