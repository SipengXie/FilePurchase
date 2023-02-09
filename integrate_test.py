from sender import Sender
from file_reader import *
from receiver import Receiver
import deploy_contract
import call_contratct
import time

key    = b'\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88\x88'

def Case_off_chain(n, length):
    plain_chunks = chunklize("big_file", length, 32)
    encrypted_chunks = chunklize("c_big_file", length, 32)
    encrypted_chunks_prime = chunklize("c_prime_big_file", length, 1)

    sender = Sender(n, length, key)
    receiver = Receiver(n, length)

    fileRoot, encrypted_path, h_C, H_H_C_plus_one, H_C_plus_one = sender.workWithEncryptedFile(plain_chunks=plain_chunks, encrypted_chunks=encrypted_chunks, encrypted_chunks_prime=encrypted_chunks_prime)
    print("Case: n =",n,"length =",length)
    print("fileRoot =",fileRoot.hex())
    print("H(C) =", h_C.hex())
    print("H(H(C+1)) =", H_H_C_plus_one.hex())
    print("H(C+1) =", H_C_plus_one)
    print("------------Sender done!-------------")

    # calcultate cipher tree
    receiver.receive_cipherText(encrypted_chunks=encrypted_chunks, encrypted_plain_tree_path=encrypted_path)
    # simulate decryption
    receiver.chunks = plain_chunks
    receiver.decrypt_only_path(key)

    print("------------ComplainAboutFileRoot------------")
    Zm, Proof = receiver.complain_about_fileRoot()
    f = open("complainAboutFileRoot-{n}-{length}".format(n=n, length=length),"w")
    f.write("{Zm}\n".format(Zm=Zm))
    f.write("{Proof}".format(Proof=Proof))
    f.close()
    print("------------ComplainAboutLeaf------------")
    Zin_1, Zin_2, Zout, proofIn_1, _, proofOut = receiver.complain_about_chunk(in_1=0, in_2=1, out=n)
    f = open("complainAboutLeaf-{n}-{length}".format(n=n, length=length),"w")
    f.write("{indexOut}\n".format(indexOut = n)) # index out
    f.write("{indexIn}\n".format(indexIn = 0)) # index in
    f.write("{Zin_1}\n".format(Zin_1 = Zin_1))
    f.write("{Zin_2}\n".format(Zin_2 = Zin_2))
    f.write("{Zout}\n".format(Zout = Zout))
    f.write("{proofIn_1}\n".format(proofIn_1 = proofIn_1))
    f.write("{proofOut}".format(proofOut = proofOut))
    print("------------ComplainAboutNode------------")
    Zin_1, Zin_2, Zout, proofIn_1, _, proofOut = receiver.complain_node(in_1 = n, in_2 = n + 1, out = n + n // 2)
    f = open("complainAboutNode-{n}-{length}".format(n=n, length=length),"w")
    f.write("{indexOut}\n".format(indexOut = n + n // 2)) # index out
    f.write("{indexIn}\n".format(indexIn = n)) # index in
    f.write("{Zin_1}\n".format(Zin_1 = Zin_1))
    f.write("{Zin_2}\n".format(Zin_2 = Zin_2))
    f.write("{Zout}\n".format(Zout = Zout))
    f.write("{proofIn_1}\n".format(proofIn_1 = proofIn_1))
    f.write("{proofOut}".format(proofOut = proofOut))

def Case_on_chain(n, length):
    contract_address = deploy_contract.run(n, length)
    caller = call_contratct.caller(n, length, contract_address)
    time.sleep(15)
    caller.accept(b'Gxa\xdb\xef\x98\x9d\xbfog\xa5>b+@?\x16\xed4LG\xc9D\xbb\xad7\xa9v\xd2\x14\xc3\x13') # filled with H(C+1)
    time.sleep(15)
    caller.keyReveal(key)

    print("------------ComplainAboutFileRoot------------")
    f = open("complainAboutFileRoot-{n}-{length}".format(n=n, length=length),"r")
    Zm = eval(f.readline()[:-1])
    proof = eval(f.readline())
    f.close()
    caller.complainFileRoot(Zm=Zm, Proof=proof)

    print("------------ComplainAboutLeaf------------")
    f = open("complainAboutLeaf-{n}-{length}".format(n=n, length=length),"r")
    indexOut = eval(f.readline()[:-1])
    indexIn = eval(f.readline()[:-1])
    Zin_1 = eval(f.readline()[:-1])
    Zin_2 = eval(f.readline()[:-1])
    Zout = eval(f.readline()[:-1])
    proofIn_1 = eval(f.readline()[:-1])
    proofOut = eval(f.readline())
    f.close()
    caller.complainChunk(indexIn=indexIn, indexOut=indexOut, Zin_1=Zin_1, Zin_2=Zin_2,Zout=Zout,proofIn_1=proofIn_1,proofOut=proofOut)

    print("------------ComplainAboutNode------------")
    f = open("complainAboutNode-{n}-{length}".format(n=n, length=length),"r")
    indexOut = eval(f.readline()[:-1])
    indexIn = eval(f.readline()[:-1])
    Zin_1 = eval(f.readline()[:-1])
    Zin_2 = eval(f.readline()[:-1])
    Zout = eval(f.readline()[:-1])
    proofIn_1 = eval(f.readline()[:-1])
    proofOut = eval(f.readline())
    f.close()
    caller.complainNode(indexIn=indexIn, indexOut=indexOut, Zin_1=Zin_1, Zin_2=Zin_2,Zout=Zout,proofIn_1=proofIn_1,proofOut=proofOut)

    caller.noComplain()


if __name__ == "__main__":
    Case_off_chain(8388608, 4)
    # Case_on_chain(8388608, 4)