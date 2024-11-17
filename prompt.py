# Prompts Claude 3 using bedrock client and adds summary to database

from main import connect, get_transcript
import boto3
import requests
import psycopg2
import jsonify
from botocore.exceptions import ClientError
from datetime import datetime


client = boto3.client(
        'bedrock-runtime',
        region_name='us-west-2',
        aws_access_key_id="AKIAXDLIJXV3AI25IXPZ",
        aws_secret_access_key="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"
        )

prompt = "Make a short bullet point summary of the conversation with personal data removed and then rate the scenario as either common or extreme"
context = "EMTs are responding to a scene and need a professional summary that highlights medical needs"

transcription = []
transcript = get_transcript()
for i in transcript:
    transcription.append(i[2])

conversation = [
    {
        "role": "user",
        "content": [{"text": f"Instruction: {prompt}\n\nContext: {context}\n\nInput:\n{transcription}"}],
    }
]

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
    exit(1)

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
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO TRANSCRIPT (SUMMARY, PRIORITY) VALUES (%s , %s)', (summary_lines, rating)) # SQL Insert Command to db
    conn.commit()
    print('message: success')

except Exception as e:
    print('error: '+str(e))

finally:
    cursor.close()
