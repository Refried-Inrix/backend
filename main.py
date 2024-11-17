from flask import Flask, request, jsonify
import time
import boto3
import threading
import os
import psycopg2
import json
# import atexit

app = Flask(__name__)

# Constants
PORT = 5432
REGION = "us-west-2"
SECRET_NAME = "DBAccess"

# Function to get the secret from AWS Secrets Manager
def get_secret():
    session = boto3.session.Session()
    client = session.client("secretsmanager", region_name=REGION)

    try:
        # Fetch the secret value
        response = client.get_secret_value(SecretId=SECRET_NAME)
        # Parse the secret as JSON
        secret = json.loads(response["SecretString"])
        return secret
    except Exception as e:
        print(f"Error retrieving secret {SECRET_NAME}: {e}")
        return None

# Fetch the secret
user_secret = get_secret()

if user_secret:
    # Extract the secrets
    try:
        PASSWORD = user_secret["SecrPassword"] 
        USER = user_secret["SecrUser"]        
        ENDPOINT = user_secret["SecrEndpoint"] 
        print("Successfully retrieved secrets from Secrets Manager.")
    except KeyError as e:
        print(f"Missing key in secret: {e}. Ensure the secret contains all required keys.")
        PASSWORD, USER, ENDPOINT = None, None, None
else:
    print("Failed to retrieve the secret.")
    PASSWORD, USER, ENDPOINT = None, None, None

# Database connection function
def connect():
    """Connect to the PostgreSQL database."""
    if not PASSWORD or not USER or not ENDPOINT:
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

        cursor = conn.cursor() #dictionary=True\    
        print("Successfully connected to the database.")

        #  cursor.execute("""
        #      CREATE TABLE TRANSCRIPT (
        #        DATE VARCHAR(255),
        #        MESSAGE VARCHAR(255)
        #      );
        # """)
        
        return conn
    except psycopg2.Error as e:
        print(f"Error connecting to the database: {e}")
        return None

"""== Globals ============================================="""
conn = connect()
# threads = []
# client = boto3.client('rds', region_name=REGION, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
# token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)
"""========================================================"""

# def worker(num):
#     """thread worker function"""
#     print(f'Worker: {num}')
#
# def init():
#     """init the global state"""
#     t = threading.Thread(target=worker, args=(1,))
#     t.start()
#     threads.append(t);
#
# def deinit():
#     print("atexit")
#     for t in threads:
#         t.join()

@app.route("/")
def index():
    return "<p>Use the /api endpoint</p>"

# Read endpoint get all transcripts
@app.route('/api/v1/transcript', methods=['GET'])
def get_transcript():
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM TRANSCRIPT')
        transcript = cursor.fetchall()
        return jsonify(transcript)
    except Exception as e:
        return jsonify({'error': str(e)})

# Write endpoint to add new transcript
@app.route('/api/v1/transcript', methods=['POST'])
def add_transcipt():
    try:
        cursor = conn.cursor()

        data = request.get_json()
        date = data['date']
        # author = data['author']
        msg = data['message']

        cursor.execute('INSERT INTO TRANSCRIPT (DATE, MESSAGE) VALUES (%s, %s)', (date, msg))
        conn.commit()

        return jsonify({'message': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    # init()
    # atexit.register(deinit) # this triggers on reload of flask
    app.run(host="0.0.0.0", port=5000) # debug=True)

