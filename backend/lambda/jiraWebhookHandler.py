import json
import boto3
import os
import logging
from pinecone import Pinecone
from models import IssueVector

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret(secret_arn):
    logger.info(f"Fetching secret with ARN: {secret_arn}")
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_arn)
        secrets = json.loads(response["SecretString"])
        logger.info("Secrets retrieved successfully.")
        return secrets
    except Exception as e:
        logger.error(f"Error retrieving secret: {str(e)}", exc_info=True)
        raise

# 
pinecone_secret_arn = os.getenv("PINECONE_SECRET_ARN")
secrets = get_secret(pinecone_secret_arn)

PINECONE_API_KEY = secrets["apiKey"]
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_URL")

pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
index = pc.Index(host=PINECONE_INDEX_NAME)

logger.info("Checking Pinecone index status...")
index_status = index.describe_index_stats()
logger.info(f"Index status: {index_status}")

bedrock_runtime = boto3.client("bedrock-runtime")

def generate_embedding(text: str):
    logger.info("Generating embedding for the text...")
    try:
        response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({"inputText": text}),
            accept="application/json",
            contentType="application/json"
        )
        embedding = json.loads(response["body"].read())["embedding"]
        logger.info("Embedding generated successfully.")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {str(e)}", exc_info=True)
        raise

def lambda_handler(event, context):
    logger.info(f"Lambda function invoked. Request ID: {context.aws_request_id}")

    try:
        body = json.loads(event["body"])
        event_type = body.get("webhookEvent")
        issue = body.get("issue")
        comment = body.get("comment")

        if not issue:
            logger.warning("Invalid event data - missing issue.")
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
        logger.info(f"Processing issue with ID: {text_id}")
        embedding = generate_embedding(issue_text_sum)

        issue_vector = IssueVector(text_id, embedding, issue_text_sum, base_url + issue_key)

        logger.info(f"Event type received: {event_type}")

        if event_type in ["jira:issue_created", "jira:issue_updated", "jira:comment_added"]:
            logger.info(f"Upserting vector with ID: {text_id}")
            index.upsert(vectors=[issue_vector.to_dict()], namespace="jira")
            logger.info(f"Vector {text_id} inserted successfully.")
            return {"statusCode": 200, "body": json.dumps({"message": "Ticket processed", "issue_id": issue_id})}

        elif event_type in ["jira:issue_deleted", "jira:comment_deleted"]:
            logger.info(f"Deleting vector with ID: {text_id}")
            index.delete(ids=[text_id], namespace="jira")
            return {"statusCode": 200, "body": json.dumps({"message": "Ticket deleted", "issue_id": issue_id})}

        logger.info(f"Event processed: {event_type}")
        return {"statusCode": 200, "body": json.dumps({"message": "Event processed", "event_type": event_type})}

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}", exc_info=True)
        return {"statusCode": 500, "body": json.dumps(f"Error occurred: {str(e)}")}
    
