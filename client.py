from socket import AF_INET, socket, SOCK_STREAM
import base64
from threading import Thread
import tkinter
import json
import random
from math import sqrt; from itertools import count, islice

def receive():
    while True:
        rawmsg = json.loads(client_socket.recv(1024).decode("utf8"))
        if rawmsg['type'] == 'msg':
            print('What i recieved: '+ rawmsg['text'])
            print('What i decode: '+ decrypt(rawmsg['text']))
            messages.insert(tkinter.END, decrypt(rawmsg['text']))
        if rawmsg['type'] == 'int':
            messages.insert(tkinter.END, rawmsg['text'])
            global sharedKey
            global init
            global cleintKeyPublic
            b=random.randint(1,rawmsg['p2']-1)
            cleintKeyPublic = pow(rawmsg['p1'],b,rawmsg['p2'])
            sharedKey= str(pow(rawmsg['key'],b,rawmsg['p2']))
            print('Secret Shared Key = ' +sharedKey)
            init=True



def send(event=None):
    global init
    if init:
        rawmsg = json.dumps({
            'type':'init',
            'text': encrypt(textMessage.get()),
            'key': cleintKeyPublic
            })
        
        init = False
    else:
        rawmsg = encrypt(json.dumps({
            'type':'msg',
            'text': textMessage.get()
            }))
    textMessage.set("") 
    client_socket.send(bytes(rawmsg, "utf8"))
    if rawmsg == "!quit":
        client_socket.close()
        top.quit()


def close(event=None):
    textMessage.set("!quit")
    send()




def encrypt(message):
    encoded_chars = []
    for i in range(len(message)):
        key_c =sharedKey[i % len(sharedKey)]
        encoded_c = chr(ord(message[i]) + ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string

def decrypt(message):
    encoded_chars = []
    for i in range(len(message)):
        key_c =sharedKey[i % len(sharedKey)]
        encoded_c = chr(ord(message[i]) - ord(key_c) % 256)
        encoded_chars.append(encoded_c)
    encoded_string = "".join(encoded_chars)
    return encoded_string



top = tkinter.Tk()
messages_frame = tkinter.Frame(top)
textMessage = tkinter.StringVar() 
scrollbar = tkinter.Scrollbar(messages_frame)  
messages = tkinter.Listbox(messages_frame, height=20, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
messages.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
messages.pack()
messages_frame.pack()
top.title("Encyrpted Chat")
entry_field = tkinter.Entry(top, textvariable=textMessage)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()
init=False
top.protocol("WM_DELETE_WINDOW", close)
sharedKey = 0
ADDR = ('127.0.0.1', 50000)
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.