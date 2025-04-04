import json
import boto3
import requests
import logging
from requests.auth import HTTPBasicAuth
import os
from pinecone import Pinecone
from models import IssueVector

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_secret(secret_arn):
    try: 
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_arn)
        secret = json.loads(response["SecretString"])
        logger.info("Secret retrieved successfully.")
        return secret
    except Exception as e:
        logger.error(f"Error retrieving secret: {e}")
        raise

bedrock_runtime = boto3.client("bedrock-runtime")
secret_arn = os.getenv("PINECONE_SECRET_ARN")
secrets = get_secret(secret_arn)

PINECONE_API_KEY = secrets["apiKey"]
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_URL")

logger.info("Initializing Pinecone client.")
pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
index = pc.Index(host=PINECONE_INDEX_NAME)
logger.info(f"Pinecone index '{PINECONE_INDEX_NAME}' initialized.")

index_status = index.describe_index_stats()
logger.info(f"Index stats: {index_status}")

def generate_text_embedding(text: str):
    try:
        logger.info("Generating text embedding.")
        embedding_response = bedrock_runtime.invoke_model(
            modelId="amazon.titan-embed-text-v2:0",
            body=json.dumps({"inputText": text}),
            accept="application/json",
            contentType="application/json"
        )        
        embedding = json.loads(embedding_response["body"].read())["embedding"]
        logger.info("Text embedding generated successfully.")
        return embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise

def handler(event, context):
    print("USAO JE U HANDLER")
    secret_arn = os.getenv("JIRA_SECRET_ARN")
    secrets = get_secret(secret_arn)

    JIRA_API_TOKEN = secrets["JIRA_API_TOKEN"]
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_URL = os.getenv("JIRA_URL")
    JIRA_URL_COMMENTS = os.getenv("JIRA_URL_COMMENTS")

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
  
    try:
        startAt = 0
        response = requests.get(f"{JIRA_URL}startAt={startAt}", auth=auth)
        logger.info("Fetching JIRA issues.")

        while len(response.json().get('issues')) != 0:
            logger.info(f"Processing issues batch starting at {startAt}")

            response_with_comments = requests.get(JIRA_URL_COMMENTS, auth=auth)

            if response.status_code == 200 and response_with_comments.status_code == 200:
                format_and_insert_issues(response.json(), response_with_comments.json())
            else:
                if response.status_code == 200:
                    logger.error(f"Error fetching tickets: {response.status_code}")
                    return {
                        'statusCode': response_with_comments.status_code,
                        'body': json.dumps('Error fetching tickets comments from JIRA.')
                    }
                else:
                    logger.error(f"Error fetching ticket comments: {response_with_comments.status_code}")
                    return {
                        'statusCode': response.status_code,
                        'body': json.dumps('Error fetching tickets from JIRA.')
                    }
            startAt += 100
            response = requests.get(f"{JIRA_URL}startAt={startAt}", auth=auth)
        logger.info("All issues processed successfully.")
        return {
            'statusCode': 200,
            'body': json.dumps({"message": "Data inserted into Pinecone"})
            }
       

    except Exception as e:
        logger.exception(f"Unhandled exception in handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error occurred: {str(e)}')
        }
    
def format_and_insert_issues(issues_data, comments_data):
    base_url = "https://jiralevi9internship2025.atlassian.net/browse/"
    comments_mapping = { issue["id"]: issue["fields"]["comment"]["comments"] for issue in comments_data.get("issues", [])}     

    subtasks = []
    for issue in issues_data.get("issues", []):
        fields = issue.get("fields", {})
        
        if fields['issuetype']['subtask']:
            continue

        issue_id = issue.get("id")
        issue_text_sum = f"{issue.get('key')} - {fields.get('summary', '')}\n{fields.get('description', '')} creator: {fields.get('creator', {}).get('displayName', '')}"
        
        if fields['subtasks']: issue_text_sum += ', subtasks: '
        for subtask in fields['subtasks']:
            issue_text_sum += f" {subtask['key']} - {subtask['fields']['summary']},"

        comments = comments_mapping.get(issue_id, [])
        if comments: issue_text_sum += ", comments: "
        for comment in comments:
            issue_text_sum += " " + comment.get("body")

        text_id = issue_id

        try:
            embedding = generate_text_embedding(issue_text_sum)
            issue_vector = IssueVector(text_id, embedding, issue_text_sum, base_url + issue["key"] )
            index.upsert(vectors=[issue_vector.to_dict()], namespace="jira")

            logger.info(f"Issue {issue.get('key')} inserted into Pinecone.")
        except Exception as e:
            logger.error(f"Failed to embed or upsert issue {issue.get('key')}: {e}")

    return subtasks
