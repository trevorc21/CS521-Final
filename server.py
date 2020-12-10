from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import json
import base64
import random
from math import sqrt; from itertools import count, islice

def incoming_connections():
    global a
    global p
    while True:

        client, client_address = SERVER.accept()
        print("%s:%s Started Connection " % client_address)
        while True:
            g=gen_primes((1 * (2**int(32)/2))-1)[0]
            
            p= (g*2)+1
            
            if is_prime_number(p):
                break

        a=random.randint(1,p-1)
        g=int(g)
        p=int(p)
        client.send(bytes(json.dumps({'type':'int','text': 'Welcome, Enter your name','p1':g,'p2':p, 'key':pow(g,a,p)}), "utf8"))
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):
    global pubKey
    rawmsg = client.recv(BUFSIZ).decode("utf8")
    clientName = decrypt(json.loads(rawmsg)['text'],str(pow(json.loads(rawmsg)['key'],a,p)))
    pubKey[clientName] = str(pow(json.loads(rawmsg)['key'],a,p))
    msg = "%s Entered" % clientName
    client.send(bytes(json.dumps({'type':'msg', 'text': encrypt('Your text is now encrypted',pubKey[clientName])}), "utf8"))
    sendAllClients(msg)
    print('Secret Shared Key = ' + pubKey[clientName])
    clients[client] = decrypt(json.loads(rawmsg)['text'],pubKey[clientName])
    while True:
        rawmsg = client.recv(BUFSIZ).decode("utf8")
        print('I recieved ' + rawmsg )
        rawmsg=decrypt(rawmsg, pubKey[clients[client]])
        print('Which decodes to ' + rawmsg )
        if json.loads(rawmsg)['text'] != "!quit":
            sendAllClients(json.loads(rawmsg)['text'], clientName+": ")
        else:
            client.send("!quit")
            client.close()
            del clients[client]
            sendAllClients("%s quit" % clientName)
            break

def encrypt(message,key):
    encoded_chars = []
    for i in range(len(message)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(message[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string

def decrypt(message,key):
    encoded_chars = []
    for i in range(len(message)):
        key_c = key[i % len(key)]
        encoded_c = chr(ord(message[i]) - ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string


def sendAllClients(msg, clientName=""):
    print(clients)
    for sock in clients:
        sock.send(bytes(json.dumps({'type':'msg', 'text': encrypt(clientName+msg,pubKey[clients[sock]])}), "utf8"))  

def gen_primes(e):
    D = {}
    q = random.randint(1,e)
    stuff=[]
    while True:
        if q not in D:

            stuff.append(q)
            D[q * q] = [q]
            return stuff
        else:
            for p in D[q]:
                D.setdefault(p + q, []).append(p)
            del D[q]
        q += 1
        if q>=e:
            q = random.randint(1,e)      
    return stuff


def is_prime_number(n, k=5): # miller-rabin
    from random import randint
    if n < 2: return False
    for p in [2,3,5,7,11,13,17,19,23,29]:
        if n % p == 0: return n == p
    s, d = 0, n-1
    while d % 2 == 0:
        s, d = s+1, d/2
    for i in range(k):
        x = pow(randint(2, n-1), int(d), n)
        if x == 1 or x == n-1: continue
        for r in range(1, s):
            x = (x * x) % n
            if x == 1: return False
            if x == n-1: break
        else: return False
    return True


clients = {}
pubKey={}
pubKeyServer = str(123)
ADDR = ('', 50000)
BUFSIZ = 1024
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Ready to connect")
    thread_listener = Thread(target=incoming_connections)
    thread_listener.start()
    thread_listener.join()
    SERVER.close()