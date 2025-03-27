import json
import boto3
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv

def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return secret


def lambda_handler(event, context):

    secret_arn = os.getenv("JIRA_SECRET_ARN")
    secrets = get_secret(secret_arn)
    JIRA_API_TOKEN = secrets["JIRA_API_TOKEN"]
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_URL = os.getenv("JIRA_URL")
    
    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
  
    try:

        response = requests.get(JIRA_URL, auth=auth)

        if response.status_code == 200:
            tickets = response.json()
            print(json.dumps(tickets['issues'], indent=2))
            return {
                'statusCode': 200,
                'body': json.dumps(tickets['issues'])
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
