import json
import boto3
import requests
from requests.auth import HTTPBasicAuth
import os

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
    JIRA_URL_COMMENTS = os.getenv("JIRA_URL_COMMENTS")

    auth = HTTPBasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
  
    try:

        response = requests.get(JIRA_URL, auth=auth)
        response_with_comments = requests.get(JIRA_URL_COMMENTS, auth=auth)

        if response.status_code == 200 and response_with_comments.status_code == 200:
            tickets = filter_issues(response.json(), response_with_comments.json())
            return {
                'statusCode': 200,
                'body': json.dumps(tickets)
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

def filter_issues(issues_data, comments_data):
    filtered_issues = []

    base_url = "https://jiralevi9internship2025.atlassian.net/browse/"

    comments_mapping = { issue["id"]: issue["fields"]["comment"]["comments"] for issue in comments_data.get("issues", [])}

    for issue in issues_data.get("issues", []):
        fields = issue.get("fields", {})
        issue_id = issue.get("id")

        filtered_comments = []
        comments = comments_mapping.get(issue_id, [])

        for comment in comments:
            filtered_comment = {
                "id": comment.get("id"),
                "author": comment.get("author", {}).get("displayName"),
                "body": comment.get("body"),
                "created": comment.get("created"),
                "updated": comment.get("updated")
            }
            filtered_comments.append(filtered_comment)

        filtered_issue = {
            "id": issue.get("id"),
            "key": issue.get("key"),
            "summary": fields.get("summary"),
            "status": fields.get("status", {}).get("name"),
            "priority": fields.get("priority", {}).get("name"),
            "description": fields.get("description") if fields.get("description") else "",
            "project": fields.get("project", {}).get("name"),
            "issuetype": fields.get("issuetype", {}).get("name"),
            "creator": fields.get("creator", {}).get("displayName"),
            "assignee": fields.get("assignee", {}).get("displayName") if fields.get("assignee") else "",
            "labels": fields.get("labels", []),
            "created": fields.get("created"),
            "updated": fields.get("updated"),
            "sprint": fields.get("customfield_10020", [{}])[0].get("name") if fields.get("customfield_10020") else None,
            "comments": filtered_comments if filtered_comments else [],
            "url": base_url + issue["key"]
        }

        filtered_issues.append(filtered_issue)
    return filtered_issues