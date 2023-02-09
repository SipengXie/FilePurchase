import random
import struct
size = 1024 * 1024 * 1024 # 1 GB
f = open("big_file","wb")
for i in range (size):
    a = random.randint(0,255)
    ab = struct.pack("B",a)
    f.write(ab)
f.close()
