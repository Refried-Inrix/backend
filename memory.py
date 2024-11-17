from flask import jsonify
import json
import copy

messages = []

FILE="./thing.db"

def init():
    global messages

    file = open(FILE)
    messages = json.load(file)
    print("init msgs with " + str(len(messages)))
    file.close()

def addMessage(data):
    messages.append(data)

def getMessages():
    return messages

def cache():
    global messages

    msg = json.dumps(messages)
    file = open(FILE, "w")
    file.write(msg)
    file.close()

