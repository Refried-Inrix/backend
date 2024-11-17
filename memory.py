from flask import jsonify
import json
import copy

messages = []

FILE="./thing.db"

def init():
    global messages

    print("running init")
    file = open(FILE)
    messages = json.load(file)
    print("init msgs: " + str(messages))
    file.close()

def addMessage(data):
    messages.append(data)

def getMessages():
    return messages

def cache():
    global messages

    print("running a cache")
    msg = str(messages)
    print("thign: " + msg)
    file = open(FILE, "w")
    file.write(msg)
    file.close()

