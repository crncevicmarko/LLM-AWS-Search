import json
import boto3
import requests
import os
from dotenv import load_dotenv

JIRA_URL = 'https://jiralevi9internship2025.atlassian.net/rest/api/2/search?jql=project=SCRUM&maxResults=1000'
# JIRA API Token i email
JIRA_EMAIL = 'grubor.masa@gmail.com'
load_dotenv()

# Preuzmi token iz okruženja
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
def lambda_handler(event, context):

    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    
    try:
     
        response = requests.get(JIRA_URL, auth=auth)

        if response.status_code == 200:
            tickets = response.json()
            print(json.dumps(tickets["issues"], indent=2))
            return {
                'statusCode': 200,
                'body': json.dumps('Tickets retrieved successfully!')
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