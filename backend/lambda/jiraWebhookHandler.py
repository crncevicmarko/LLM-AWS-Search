import json
import boto3
import os
from pinecone import Pinecone
from models import IssueVector

def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    return json.loads(response["SecretString"])

# 
pinecone_secret_arn = os.getenv("PINECONE_SECRET_ARN")
secrets = get_secret(pinecone_secret_arn)

PINECONE_API_KEY = secrets["apiKey"]
PINECONE_INDEX_NAME = secrets["indexUrl"]

pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
index = pc.Index(host=PINECONE_INDEX_NAME)

print("Index status : " ,index.describe_index_stats())

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

        text_id = issue_id
        print("Id : "+text_id)
        embedding = generate_embedding(issue_text_sum)

        issue_vector = IssueVector(text_id, embedding, issue_text_sum, base_url + issue_key)

        print("Event type : ",event_type)

        if event_type in ["jira:issue_created", "jira:issue_updated", "jira:comment_added"]:
            print(f"Upserting vector with ID: {text_id}")
            index.upsert(vectors=[issue_vector.to_dict()], namespace="jira")
            print(f"Vector {text_id} inserted successfully")
            return {"statusCode": 200, "body": json.dumps({"message": "Ticket processed", "issue_id": issue_id})}

        elif event_type in ["jira:issue_deleted", "jira:comment_deleted"]:
            index.delete(ids=[text_id], namespace="jira")
            return {"statusCode": 200, "body": json.dumps({"message": "Ticket deleted", "issue_id": issue_id})}

        return {"statusCode": 200, "body": json.dumps({"message": "Event processed", "event_type": event_type})}

    except Exception as e:
        return {"statusCode": 500, "body": json.dumps(f"Error occurred: {str(e)}")}
    
