import boto3
import hashlib
import json
import os
from pinecone import (
    Pinecone
)
from models import IssueVector

bedrock_runtime = boto3.client("bedrock-runtime")

def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return secret

def generate_text_embedding(text: str):
    embedding_response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text}),
        accept="application/json",
        contentType="application/json"
    )
    return json.loads(embedding_response["body"].read())["embedding"]

def handler(event, context):
    try:

        secret_arn = os.getenv("PINECONE_SECRET_ARN")
        secrets = get_secret(secret_arn)

        PINECONE_API_KEY = secrets["apiKey"]
        PINECONE_INDEX_NAME = secret_arn["indexUrl"]

        pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
        index = pc.Index(host=PINECONE_INDEX_NAME)

        body = event["body"]
        text = body.get("text")

        if not text:
            return {"statusCode": 400, "body": "Missing 'text' parameter"}

        text_id = f"{hashlib.md5(text.encode()).hexdigest()}"

        embedding = generate_text_embedding(text)
        
        issue_vector = IssueVector(text_id, embedding, text, "asdfa")
        index.upsert(vectors=[issue_vector.to_dict()], namespace="jira")

        return {"statusCode": 200, "body": json.dumps({"message": "Data inserted into Pinecone", "id": text_id})}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
