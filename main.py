from flask import Flask, request, jsonify
import time
import boto3
import threading
import atexit
import json
import os
import psycopg2

app = Flask(__name__)

ENDPOINT='database-1.cluster-cr20c6qq8ktf.us-west-2.rds.amazonaws.com'
# ENDPOINT='database-1.cluster-ro-cr20c6qq8ktf.us-west-2.rds.amazonaws.com' # READONLY
PORT=5432
USER='refriedpostgres'
REGION='us-west-2'
DBNAME='database-1'

"""== Globals ============================================="""
threads = []
client = boto3.client('rds', region_name=REGION, aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key)
token = client.generate_db_auth_token(DBHostname=ENDPOINT, Port=PORT, DBUsername=USER, Region=REGION)
"""========================================================"""

# def worker(num):
#     """thread worker function"""
#     print(f'Worker: {num}')
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

def connect():
    return psycopg2.connect(
        host=ENDPOINT, port=PORT, database=DBNAME, user=USER, password=token, 
        # sslrootcert="/home/focus/dev/refried/us-west-2-bundle.pem"
        )

@app.route("/")
def index():
    try:
        print("1")
        # hangs forever
        conn = connect()
        print("2")

        # with connection.cursor() as cursor:
        #     cursor.execute('SELECT %s + %s AS sum', (3, 2))
        #     result = cursor.fetchone()

        cur = conn.cursor()
        cur.execute("""SELECT now()""")
        query_results = cur.fetchall()
        print("3")
        print(query_results)
    except Exception as e:
        # print("Database connection failed due to {}".format(e))          
        return jsonify({'error': str(e)}) # Return an error message if an exception occurs 


# return "<p>Use the /api endpoint</p>"

# Read endpoint get all transcripts
@app.route('/api/v1/transcript', methods=['GET'])
def get_transcript():
    # try:
    #     cursor = connection.cursor(dictionary=True)
    #
    #     cursor.execute('SELECT * FROM TRANSCRIPT')
    #     transcript = cursor.fetchall()
    #
    #     return jsonify(transcript)
    # except Exception as e:
    #     return jsonify({'error': str(e)})
    # finally:
    #     cursor.close()
    return jsonify({'message': "example response"})

# Write endpoint add new transcript
@app.route('/api/v1/transcript', methods=['POST'])
def add_transcipt():
    # try:
    #     conn = connect()
    #     cursor = conn.cursor()
    #
    #     data = request.get_json()
    #     date = data['date']
    #     # author = data['author']
    #     msg = data['message']
    #
    #     cursor.execute('INSERT INTO TRANSCRIPT (DATE, MESSAGE) VALUES (%s, %s)', (date, msg))
    #     conn.commit()
    #
    #     return jsonify({'message': 'success'})
    # except Exception as e:
    #     return jsonify({'error': str(e)})
    # finally:
    #     cursor.close()
    return jsonify({'message': "example response"})

if __name__ == '__main__':
    # init()
    # atexit.register(deinit) # this triggers on reload of flask
    app.run(host="0.0.0.0", port=5000, debug=True)


