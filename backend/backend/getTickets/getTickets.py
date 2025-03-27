import json
import boto3
import requests
from requests.auth import HTTPBasicAuth
import os
from dotenv import load_dotenv,find_dotenv

def lambda_handler(event, context):

    env_path=".env"
    load_dotenv(dotenv_path=env_path)
    
    JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
    JIRA_EMAIL = os.getenv("JIRA_EMAIL")
    JIRA_URL=os.getenv("JIRA_URL")
    
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