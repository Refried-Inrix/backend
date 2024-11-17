from flask import Flask, request, jsonify
import time
import boto3
import threading
import os
import psycopg2

# import json
# import atexit

app = Flask(__name__)

# READONLY: 'database-1.cluster-ro-cr20c6qq8ktf.us-west-2.rds.amazonaws.com' 
ENDPOINT='database-1.cluster-cr20c6qq8ktf.us-west-2.rds.amazonaws.com'
PORT=5432
USER='refriedpostgres'
REGION='us-west-2'

def connect():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    ssl = dir_path + "/etc/us-west-2-bundle.pem"
    conn = psycopg2.connect(
            host=ENDPOINT,
            port=PORT,
            database="postgres",
            user=USER,
            password='TODO',
            sslrootcert=ssl,
            sslmode="require"
        )

    cursor = conn.cursor()

    # cursor.execute("""
    #   CREATE TABLE TRANSCRIPT (
    #     DATE VARCHAR(255),
    #     MESSAGE VARCHAR(255)
    #   );
    # """)

    # year INT

    return conn

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

