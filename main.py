from flask import Flask, request, jsonify, Response
import time
import boto3
import json
import requests
from botocore.exceptions import ClientError
from datetime import datetime
import logging

if True:
    import memory as db
else:
    import database as db


from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# import search

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


# Write endpoint to add new msgs
@app.route('/api/v1/transcript', methods=['POST', 'OPTIONS'])
def post_transcipt():
    try:
        data = request.get_json()

        try:
            print("message from: " + str(data["author"]))
        except Exception as e:
            print(f"error: {e}")

        db.addMessage(data)

        print("caching messages")
        msgs = db.getMessages()
        if (len(msgs) % 10 == 0):
            db.cache()

        return jsonify({'message': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})


cachedresults = {}

@app.route('/api/v1/summary', methods=['GET'])
def get_summary(): # index
    global cachedresults

    targetAuthor = request.args.get('author', default = "all", type=str)

    client = boto3.client(
            'bedrock-runtime',
            region_name=REGION,
            aws_access_key_id=ACCESSID,
            aws_secret_access_key=ACCESSKEY
        )

    prompt = "Make a short bullet point summary of the conversation with personal data removed and then rate the scenario as either common or extreme"
    context = "EMTs are responding to a scene and need an accurate summary that highlights any medical needs"

    transcription = []
    msgs = db.getMessages()
    outputTime = ""

    for i in msgs:
        if targetAuthor == "all" or i["author"] == targetAuthor:
            outputTime = i["date"]
            transcription.append(i["message"])

    if (len(transcription) == 0):
        return jsonify({'summaries': ["nothing has happend yet"], "author": targetAuthor})

    transcription = "".join(transcription)

    h = str(hash(transcription))
    if (h in cachedresults):
        print("using chached query")
        return jsonify(cachedresults[h])

    conversation = [{
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

    # timestamp = datetime.now()
    # data = f"\nTimestamp: {timestamp}, Location: {Location}\n{summary_lines}\n\n"

    try:
        # cursor = conn.cursor()
        # cursor.execute('INSERT INTO PARSED (SUMMARY, PRIORITY) VALUES (%s , %s)', (summary_lines, rating))
        # conn.commit()

        print('message summary: success')

        sum = {
            'summaries': summary_lines,
            'time': outputTime,
            'author': targetAuthor
        }
        cachedresults[h] = sum
        # print(sum)
        return jsonify(sum)

    except Exception as e:
        print('error: '+ str(e))
        return jsonify({'error': str(e)})

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', default = "intrest", type=str)

    client = boto3.client(
            'bedrock-runtime',
            region_name=REGION,
            aws_access_key_id=ACCESSID,
            aws_secret_access_key=ACCESSKEY
            )

    prompt = {query}
    context = "Find any relevant information from the data from the prompt "

    data = db.getMessages()

    req= [
        {
            "role": "user",
            "content": [{"text": f"Instruction: {prompt}\n\nContext: {context}\n\nData:\n{data}"}],
        }
    ]
    try:
        response = client.converse(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            messages=req,
            inferenceConfig={"maxTokens":4096,"stopSequences":["User:"],"temperature":0,"topP":1},
            additionalModelRequestFields={}
        )

        response_text = response["output"]["message"]["content"][0]["text"]
        print(response_text)

    except (ClientError, Exception) as e:
        print(f"ERROR: Can't invoke model. Reason: {e}")
        return jsonify({'error': "invalid permissions"})

    results = {
        'query': query,
        'results': [ response_text ]
    }

    return jsonify(results)

# from OpenSSL import SSL
# context = SSL.Context(SSL.PROTOCOL_TLSv1_2)
# context.use_privatekey_file('server.key')
# context.use_certificate_file('server.crt')

if __name__ == '__main__':
    db.init()
    app.run(host="0.0.0.0", port=5000)

