import json
import boto3
import hashlib
import os
from requests.auth import HTTPBasicAuth
from pinecone import Pinecone

# from models import IssueVector

def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])

# Dohvatanje tajni
pinecone_secret_arn = os.getenv("PINECONE_SECRET_ARN")
secrets = get_secret(pinecone_secret_arn)

PINECONE_API_KEY = secrets["apiKey"]
PINECONE_INDEX_NAME = secrets["indexUrl"]

# Inicijalizacija Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
index = pc.Index(host=PINECONE_INDEX_NAME)

# Inicijalizacija AWS Bedrock
bedrock_runtime = boto3.client("bedrock-runtime")

def generate_embedding(text: str):
    response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text}),
        accept="application/json",
        contentType="application/json"
    )
    return json.loads(response["body"].read())["embedding"]

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])
        event_type = body.get("webhookEvent")
        issue = body.get("issue")
        comment = body.get("comment")

        if not issue:
            return {"statusCode": 400, "body": "Invalid event data - missing issue"}

        issue_id = issue["id"]
        issue_key = issue["key"]
        summary = issue["fields"].get("summary", "")
        description = issue["fields"].get("description", "")
        creator = issue["fields"].get("creator", {}).get("displayName", "")

        base_url = "https://jiralevi9internship2025.atlassian.net/browse/"
        issue_text_sum = f"{summary}\n{description}{issue_key} creator: {creator}"

        if comment:
            issue_text_sum += " " + comment["body"]

        text_id = hashlib.md5(issue_text_sum.encode()).hexdigest()
        print("Id : "+text_id)
        embedding = generate_embedding(issue_text_sum)

        issue_vector = IssueVector(text_id, embedding, issue_text_sum, base_url + issue_key)

        if event_type in ["issue_created", "issue_updated", "comment_added"]:
            index.upsert(vectors=[issue_vector.to_dict()], namespace="jira")
            return {"statusCode": 200, "body": json.dumps({"message": "Ticket processed", "issue_id": issue_id})}

        elif event_type in ["issue_deleted", "comment_deleted"]:
            index.delete(ids=[text_id], namespace="jira")
            return {"statusCode": 200, "body": json.dumps({"message": "Ticket deleted", "issue_id": issue_id})}

        return {"statusCode": 200, "body": json.dumps({"message": "Event processed", "event_type": event_type})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error occurred: {str(e)}")}
    
from typing import List, Dict

class IssueVector:
    def init(self, text_id: str, embedding: List[float], text: str, url: str):
        self.id = text_id
        self.values = embedding
        self.metadata = {
            "text": text,
            "length": len(text),
            "ticket-url": url
        }

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "values": self.values,
            "metadata": self.metadata
        }
