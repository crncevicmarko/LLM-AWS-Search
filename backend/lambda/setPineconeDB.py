import boto3
import hashlib
import json
import os
from pinecone import (
    Pinecone
)


def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return secret


secret_arn = os.getenv("PINECONE_SECRET_ARN")
secrets = get_secret(secret_arn)

PINECONE_API_KEY = secrets["apiKey"]
PINECONE_INDEX_NAME = os.environ["indexUrl"]

pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
index = pc.Index(host=PINECONE_INDEX_NAME)

bedrock_agent = boto3.client("bedrock-agent")

def handler(event, context):
    try:
        body = event["body"]
        text = body.get("text")

        if not text:
            return {"statusCode": 400, "body": "Missing 'text' parameter"}

        text_id = f"text-{hashlib.md5(text.encode()).hexdigest()}"

        bedrock_runtime = boto3.client("bedrock-runtime")

        embedding_response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({"inputText": text}),
            accept="application/json",
            contentType="application/json"
        )

        embedding = json.loads(embedding_response["body"].read())["embedding"]

        index.upsert(
        vectors=[
            {
                "id": text_id,  
                "values": embedding,  
                "metadata": {
                    "text": text,  
                    "length": len(text)  
                }
            }
            ],
            namespace="jira"  
        )

        return {"statusCode": 200, "body": json.dumps({"message": "Data inserted into Pinecone", "id": text_id})}

    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
