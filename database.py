from flask import jsonify
import json
import copy
import boto3

REGION = "us-west-2"
ENDPOINT='database-1.cluster-cr20c6qq8ktf.us-west-2.rds.amazonaws.com'
PORT = 5432
USER='refriedpostgres'

SECRETNAME = "DBAccess"
PASSWORD = None

def __connect():
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

    return conn


def init():
    global PASSWORD

    secrets = boto3.client("secretsmanager", region_name=REGION)
    response = secrets.get_secret_value(SecretId=SECRETNAME)
    secret = json.loads(response["SecretString"])
    PASSWORD = secret["SecrPassword"]

    conn = __connect()
    cursor = conn.cursor()

    # cursor.execute("""
    #   CREATE TABLE IF NOT EXISTS TRANSCRIPT (
    #     DATE VARCHAR(63),
    #     MESSAGE VARCHAR(255)
    #   );
    # """)

    noop

def addMessage(data):
    conn = __connect()

    date = data['date']
    msg = data['message']
    # author = data['author']

    cursor = conn.cursor()
    cursor.execute('INSERT INTO TRANSCRIPT (DATE, MESSAGE) VALUES (%s, %s)', (date, msg))
    conn.commit()

def getMessages():
    conn = __connect()

    cursor = conn.cursor()
    cursor.execute('SELECT * FROM TRANSCRIPT')
    transcript = cursor.fetchall()
    return transcript

def cache():
    noop

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
