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

from flask_cors import CORS
app = Flask(__name__)
CORS(app)

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
        PASSWORD = user_secret["SecrPassword"] 
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


# Database connection function
def connect():
    """Connect to the PostgreSQL database."""
    if not PASSWORD or not ACCESSID or not ACCESSKEY:
        print("Missing database credentials. Cannot connect.")
        return None

    # SSL Certificate path
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ssl = dir_path + "/etc/us-west-2-bundle.pem"
    try:
        # Establish the connection
        conn = psycopg2.connect(
            host=ENDPOINT,
            port=PORT,
            database="postgres",
            user=USER,
            password=PASSWORD,
            sslrootcert=ssl,
            sslmode="require"
        )


        cursor = conn.cursor()
        print("Successfully connected to the database.")

        # cursor.execute("""
        #     DROP DATABASE TRANSCRIPT;
        # """)
        # conn.commit()

        # IF NOT EXISTS 
        # INDEX SERIAL,

        # cursor.execute(f"""
        #     CREATE TABLE {TABLENAME} (
        #       DATE VARCHAR(63),
        #       MESSAGE VARCHAR(2047),
        #       AUTHOR VARCHAR(63),
        #       LOCATIONX REAL,
        #       LOCATIONY REAL
        #     );
        # """)
        # conn.commit()

        # cursor.execute("""
        #     CREATE TABLE IF NOT EXISTS PARSED (
        #       PRIORITY VARCHAR(31),
        #       SUMMARY VARCHAR(255)
        #     );
        # """)
        conn.commit()
        cursor.close()

        return conn

    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

"""== Globals ============================================="""
# threads = []
# client = boto3.client('rds', region_name=REGION, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
# token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)
"""========================================================"""

@app.route("/")
def index():
    return "<p>Use the /api endpoint</p>"


messages = []
def addMessage(data):
    # print(f"message from: {data.author}")
    messages.append(data)

# def __get_transcript():
#     try:
#         cursor = conn.cursor()
#         cursor.execute(f'SELECT * FROM {TABLENAME};')
#         transcript = cursor.fetchall()
#
#         return transcript
#
#         # return jsonify({
#         #     "index": transcript[0],
#         #     "date": transcript[1],
#         #     "message": transcript[2],
#         #     "author": transcript[3],
#         #     "location": {
#         #         "lat": transcript[4],
#         #         "lon": transcript[5]
#         #     }
#         # })
#
#     except Exception as e:
#         return {'error': str(e)}

# Read endpoint get all transcripts
@app.route('/api/v1/transcript', methods=['GET'])
def get_transcript():
    # trans = __get_transcript()
    print(messages)
    return jsonify(messages)

# Write endpoint to add new transcript
@app.route('/api/v1/transcript', methods=['POST', 'OPTIONS'])
def add_transcipt():
    # conn = connect()
    try:
        data = request.get_json()
        print("input data: " + str(data))

        addMessage(data)

        # date = data['date']
        # msg = data['message']
        # author = data['author']
        #
        # locations = data['location']
        # x = float(locations['lat'])
        # y = float(locations['lon'])
        #
        # cursor = conn.cursor()
        # if not locations:
        #     cursor.execute(f'INSERT INTO {TABLENAME} (DATE, MESSAGE, AUTHOR) VALUES (%s, %s, %s);', (date, msg, author))
        # else:
        #     x = locations['lat']
        #     y = locations['lon']
        #     cursor.execute(f'INSERT INTO {TABLENAME} (DATE, MESSAGE, AUTHOR, LOCATIONX, LOCATIONY) VALUES (%s, %s, %s, %d, %d);', (date, msg, author, x, y))
        #
        # conn.commit()
        # cursor.close()

        return jsonify({'message': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/v1/summary', methods=['GET'])
def get_summary(): # index
    conn = connect()
    client = boto3.client(
            'bedrock-runtime',
            region_name=REGION,
            aws_access_key_id=ACCESSID,
            aws_secret_access_key=ACCESSKEY
        )

    prompt = "Make a short bullet point summary of the conversation with personal data removed and then rate the scenario as either common or extreme"
    context = "EMTs are responding to a scene and need an accurate summary that highlights any medical needs"

    transcription = []
    transcript = __get_transcript()
    print("afaenf: " + str(transcript))


    for i in transcript:
        transcription.append(i[1])

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
        cursor = conn.cursor()
        cursor.execute('INSERT INTO PARSED (SUMMARY, PRIORITY) VALUES (%s , %s)', (summary_lines, rating))
        conn.commit()

        print('message: success')
        print(summary_lines)
        return jsonify({'ok': summary_lines})
    except Exception as e:
        print('error: '+ str(e))
        return jsonify({'error': str(e)})

    # cursor.close()

    import boto3


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

