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
    logger.info(f"Fetching secrets from Secrets Manager: {secret_arn}")
    try:
        client = boto3.client("secretsmanager")
        response = client.get_secret_value(SecretId=secret_arn)
        secret = json.loads(response["SecretString"])
        logger.info("Secrets retrieved successfully.")
        return secret
    except Exception as e:
        logger.error(f"Error retrieving secrets: {str(e)}", exc_info=True)
        raise

bedrock_runtime = boto3.client("bedrock-runtime")
secret_arn = os.getenv("PINECONE_SECRET_ARN")
secrets = get_secret(secret_arn)

PINECONE_API_KEY = secrets["apiKey"]
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_URL")

pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
index = pc.Index(host=PINECONE_INDEX_NAME)


def generate_text_embedding(text: str):
    logger.info("Generating text embedding...")
    try:
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
        logger.error(f"Error generating text embedding: {str(e)}", exc_info=True)
        raise

def handler(event, context):
    logger.info(f"Lambda invoked. Request ID: {context.aws_request_id}")
    
    secret_arn = os.getenv("JIRA_SECRET_ARN")
    secrets = get_secret(secret_arn)

    JIRA_API_TOKEN = secrets["JIRA_API_TOKEN"]
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_URL = os.getenv("JIRA_URL")
    JIRA_URL_COMMENTS = os.getenv("JIRA_URL_COMMENTS")

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
  
    try:
        logger.info(f"Fetching JIRA issues from {JIRA_URL}")
        response = requests.get(JIRA_URL, auth=auth)
        response_with_comments = requests.get(JIRA_URL_COMMENTS, auth=auth)

        if response.status_code == 200 and response_with_comments.status_code == 200:
            logger.info("JIRA issues and comments retrieved successfully.")
            format_and_insert_issues(response.json(), response_with_comments.json())

            return {
                'statusCode': 200,
                'body': json.dumps({"message": "Data inserted into Pinecone"})
            }
        else:
            if response.status_code != 200:
                logger.warning(f"Error fetching tickets: HTTP {response.status_code}")
            if response_with_comments.status_code != 200:
                logger.warning(f"Error fetching ticket comments: HTTP {response_with_comments.status_code}")
            
            return {
                'statusCode': response.status_code,
                'body': json.dumps("Error fetching tickets or comments from JIRA.")
            }
    except Exception as e:
        logger.error(f"Exception occurred: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error occurred: {str(e)}')
        }
    
def format_and_insert_issues(issues_data, comments_data):
    logger.info("Processing and inserting issues into Pinecone...")
    base_url = "https://jiralevi9internship2025.atlassian.net/browse/"
    comments_mapping = { issue["id"]: issue["fields"]["comment"]["comments"] for issue in comments_data.get("issues", [])}     

    for issue in issues_data.get("issues", []):

        fields = issue.get("fields", {})
        issue_id = issue.get("id")
        issue_text_sum = f"{fields.get('summary', '')}\n{fields.get('description', '')}{issue.get('key')} creator: {fields.get('creator', {}).get('displayName', '')}"

        comments = comments_mapping.get(issue_id, [])

        for comment in comments:

            issue_text_sum += " " + comment.get("body")

        text_id = issue_id
        embedding = generate_text_embedding(issue_text_sum)

        issue_vector = IssueVector(text_id, embedding, issue_text_sum, base_url + issue["key"] )
        try:
            index.upsert(vectors=[issue_vector.to_dict()], namespace="jira")
            logger.info(f"Issue {issue_id} inserted into Pinecone.")
        except Exception as e:
            logger.error(f"Error inserting issue {issue_id} into Pinecone: {str(e)}", exc_info=True)
    logger.info(f"All {len(issues_data.get('issues', []))} tickets are successfully inserted into Pinecone.")