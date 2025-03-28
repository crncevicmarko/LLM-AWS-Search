import json
import boto3
import hashlib
import requests
from requests.auth import HTTPBasicAuth
import os
from pinecone import Pinecone

from models import IssueVector

def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return secret

bedrock_runtime = boto3.client("bedrock-runtime")
secret_arn = os.getenv("PINECONE_SECRET_ARN")
secrets = get_secret(secret_arn)

PINECONE_API_KEY = secrets["apiKey"]
PINECONE_INDEX_NAME = secrets["indexUrl"]

pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
index = pc.Index(host=PINECONE_INDEX_NAME)


def generate_text_embedding(text: str):
    embedding_response = bedrock_runtime.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps({"inputText": text}),
        accept="application/json",
        contentType="application/json"
    )
    return json.loads(embedding_response["body"].read())["embedding"]

def handler(event, context):

    secret_arn = os.getenv("JIRA_SECRET_ARN")
    secrets = get_secret(secret_arn)

    JIRA_API_TOKEN = secrets["JIRA_API_TOKEN"]
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_URL = os.getenv("JIRA_URL")
    JIRA_URL_COMMENTS = os.getenv("JIRA_URL_COMMENTS")

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
  
    try:

        response = requests.get(JIRA_URL, auth=auth)
        response_with_comments = requests.get(JIRA_URL_COMMENTS, auth=auth)

        if response.status_code == 200 and response_with_comments.status_code == 200:
            format_and_insert_issues(response.json(), response_with_comments.json())

            return {
                'statusCode': 200,
                'body': json.dumps({"message": "Data inserted into Pinecone"})
            }
        else:
            if response.status_code == 200:
                print(f"Error fetching tickets comments: {response_with_comments.status_code}")
                return {
                    'statusCode': response_with_comments.status_code,
                    'body': json.dumps('Error fetching tickets comments from JIRA.')
                }
            else:
                print(f"Error fetching tickets: {response.status_code}")
                return {
                    'statusCode': response.status_code,
                    'body': json.dumps('Error fetching tickets from JIRA.')
                }

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f'Error occurred: {str(e)}')
        }
    
def format_and_insert_issues(issues_data, comments_data):
    base_url = "https://jiralevi9internship2025.atlassian.net/browse/"
    comments_mapping = { issue["id"]: issue["fields"]["comment"]["comments"] for issue in comments_data.get("issues", [])}     

    for issue in issues_data.get("issues", []):

        fields = issue.get("fields", {})
        issue_id = issue.get("id")
        issue_text_sum = f"{fields.get('summary', '')}\n{fields.get('description', '')}{issue.get('key')} creator: {fields.get('creator', {}).get('displayName', '')}"

        comments = comments_mapping.get(issue_id, [])

        for comment in comments:

            issue_text_sum += " " + comment.get("body")

        text_id = f"{hashlib.md5(issue_text_sum.encode()).hexdigest()}"
        embedding = generate_text_embedding(issue_text_sum)

        issue_vector = IssueVector(text_id, embedding, issue_text_sum, base_url + issue["key"] )
        index.upsert(vectors=[issue_vector.to_dict()], namespace="jira")
