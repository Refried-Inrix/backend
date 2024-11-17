from flask import Flask, request, jsonify, Response
import time
import boto3
import threading
import os
import json
# import atexit
import requests
from botocore.exceptions import ClientError
from datetime import datetime

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Constants
# PORT = 5432
REGION = "us-west-2"
SECRETNAME = "DBAccess"
# ENDPOINT='database-1.cluster-cr20c6qq8ktf.us-west-2.rds.amazonaws.com'
# USER='refriedpostgres'

# PASSWORD=None
ACCESSID=None
ACCESSKEY=None

# Function to get the secret from AWS Secrets Manager
def get_secret():
    client = boto3.client("secretsmanager", region_name=REGION)

    try:
        # Fetch the secret value
        response = client.get_secret_value(SecretId=SECRETNAME)
        # Parse the secret as JSON
        secret = json.loads(response["SecretString"])
        return secret
    except Exception as e:
        print(f"Error retrieving secret {SECRETNAME}: {e}")
        return None

# Fetch the secret
user_secret = get_secret()
if user_secret:
    # Extract the secrets
    try:
        # PASSWORD = user_secret["SecrPassword"] 
        # USER = user_secret["SecrUser"]
        # ENDPOINT = user_secret["SecrEndpoint"] 
        ACCESSID = user_secret["SecrAccessID"] 
        ACCESSKEY = user_secret["SecrKey"] 
        print("Successfully retrieved secrets from Secrets Manager.")
    except KeyError as e:
        print(f"Missing key in secret: {e}. Ensure the secret contains all required keys.")
        PASSWORD, USER, ENDPOINT, ACCESSID, ACCESSKEY = None, None, None, None, None
else:
    print("Failed to retrieve the secret.")
    PASSWORD, USER, ENDPOINT, ACCESSID, ACCESSKEY = None, None, None, None, None


messages = []

def addMessage(data):
    try:
        print("message from: " + str(data["author"]))
    except Exception as e:
        print(f"error: {e}")

    messages.append(data)

def getMessages():
    return messages


# TABLENAME="refried-thing-important-dont-forget"
# dynamo = boto3.client('dynamodb', region_name=REGION)
# dynamo.put_item(
#     TableName=TABLENAME,
#     Item={
#         'pk': {'S': 'id#1'},
#         'sk': {'S': 'cart#123'},
#         'name': {'S': 'SomeName'},
#         'inventory': {'N': '500'},
#         # ... more attributes ...
#     }
# )

# from OpenSSL import SSL
# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')

if __name__ == '__main__':
    # init()
    # atexit.register(deinit) # this triggers on reload of flask
    app.run(host="0.0.0.0", port=5000) # , ssl_context=context) # debug=True)

