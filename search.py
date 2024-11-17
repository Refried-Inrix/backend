# Prompts Claude for a summary of transcription

import boto3
from botocore.exceptions import ClientError
from flask import Flask, request, jsonify, Response
from main import db, app, get_secret

user_secret = get_secret()

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', default = "intrest", type=str)

    client = boto3.client(
            'bedrock-runtime',
            region_name='us-west-2',
            aws_access_key_id=user_secret["SecrKey"],
            aws_secret_access_key=user_secret["SecrAccessID"]
            )

    prompt = {query}
    context = "Find any relevant information from the data from the prompt "

    data = db.getMessages()

    request = [
        {
            "role": "user",
            "content": [{"text": f"Instruction: {prompt}\n\nContext: {context}\n\nData:\n{data}"}],
        }
    ]
    try:
        response = client.converse(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            messages=request,
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
        'results': [
            {response_text},
        ]
    }

    return jsonify(results)
