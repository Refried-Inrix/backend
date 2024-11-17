from flask import Flask, request, jsonify, Response
import time
import boto3
import threading
import os
import psycopg2
import json
# import atexit
import requests
from botocore.exceptions import ClientError
from datetime import datetime

if True:
    import memory as db
else:
    import database as db

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

import logging

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

# Constants
PORT = 5432
REGION = "us-west-2"
SECRETNAME = "DBAccess"
ENDPOINT='database-1.cluster-cr20c6qq8ktf.us-west-2.rds.amazonaws.com'
USER='refriedpostgres'

TABLENAME="TRANSCRIPT3"

# PASSWORD=None
# ACCESSID=None
# ACCESSKEY=None

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

"""== Globals ============================================="""
# threads = []
# client = boto3.client('rds', region_name=REGION, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
# token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)
# conn = connect()
"""========================================================"""

@app.route("/")
def index():
    return "<p>Use the /api endpoint</p>"

# Read endpoint get all transcripts
@app.route('/api/v1/transcript', methods=['GET'])
def get_transcript():
    msgs = db.getMessages()
    print("got " + str(len(msgs)) + " items")
    return jsonify(msgs)


# Write endpoint to add new transcript
@app.route('/api/v1/transcript', methods=['POST', 'OPTIONS'])
def post_transcipt():
    try:
        data = request.get_json()

        try:
            print("message from: " + str(data["author"]))
        except Exception as e:
            print(f"error: {e}")

        db.addMessage(data)

        msgs = db.getMessages()
        if (len(msgs) % 10 == 0):
            db.cache()

        return jsonify({'message': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})


# summary = ""
# summarycachelen = -1

@app.route('/api/v1/summary', methods=['GET'])
def get_summary(): # index
    # global summary
    # if (len(summary) != 0):
    #     return jsonify({'ok': summary})

    client = boto3.client(
            'bedrock-runtime',
            region_name=REGION,
            aws_access_key_id=ACCESSID,
            aws_secret_access_key=ACCESSKEY
        )

    prompt = "Make a short bullet point summary of the conversation with personal data removed and then rate the scenario as either common or extreme"
    context = "EMTs are responding to a scene and need an accurate summary that highlights any medical needs"

    transcription = []
    transcript = db.getMessages()

    for i in transcript:
        transcription.append(i["message"])

    print("transcription: " + str(transcription))
    # transcription.append(transcript[index][1])

    conversation = [ {
        "role": "user",
        "content": [{"text": f"Instruction: {prompt}\n\nContext: {context}\n\nInput:\n{transcription}"}],
    }]

    try:
        response = client.converse(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            messages=conversation,
            inferenceConfig={"maxTokens":4096,"stopSequences":["User:"],"temperature":0,"topP":1},
            additionalModelRequestFields={}
        )

        response_text = response["output"]["message"]["content"][0]["text"]

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke model. Reason: {e}")
        return jsonify({'error': "invalid permissions"})

    lines = response_text.splitlines()
    summary_started = False
    summary_lines = []
    rating = []

    for line in lines:
        if "Rating:" in line:
            rating.append(line.strip())
            rating = rating[0].split(': ')[-1]
    for line in lines:
        if "Summary:" in line:
            summary_started = True
            continue
        if summary_started:
            if line.strip() == "":
                break
            summary_lines.append(line.strip())

    summary_lines = "\n".join(summary_lines)


    #timestamp = datetime.now()
    #data = f"\nTimestamp: {timestamp}, Location: {Location}\n{summary_lines}\n\n"

    try:
        # cursor = conn.cursor()
        # cursor.execute('INSERT INTO PARSED (SUMMARY, PRIORITY) VALUES (%s , %s)', (summary_lines, rating))
        # conn.commit()

        print('message: success')
        print(summary_lines)
        summary = summary_lines
        return jsonify({'ok': {
            'summary': summary_lines,
            'time': 0,
            'author': 'name'
        }})
    except Exception as e:
        print('error: '+ str(e))
        return jsonify({'error': str(e)})

    # cursor.close()


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
    db.init()
    # init()
    # atexit.register(deinit) # this triggers on reload of flask
    app.run(host="0.0.0.0", port=5000) # , ssl_context=context) # debug=True)

