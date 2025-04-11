import json
import boto3
from botocore.exceptions import ClientError


ses_client = boto3.client('ses', region_name='eu-west-1')  
bedrock_client = boto3.client('bedrock-runtime', region_name="eu-west-1")

SENDER = "grubor.masa@gmail.com" 
RECIPIENT = "dobrosavtufegdzic@gmail.com"

SUBJECT = "Bug Report and Fix Suggestions from Chatbot App"

def handler(event, context):
    try:
        body = json.loads(event['body'])
        # user_email = body.get('email', 'Unknown')
        bug_description = body.get('description', 'No description provided.')

        fix_suggestions = get_fix_suggestions(bug_description)

        email_body = f"""
        Bug Report from Tixie:
        Bug Description: {bug_description}
        
        Possible Fix Suggestions:
        {fix_suggestions}
        """

        response = ses_client.send_email(
            Source=SENDER,
            Destination={
                'ToAddresses': [RECIPIENT],
            },
            Message={
                'Subject': {
                    'Data': SUBJECT
                },
                'Body': {
                    'Text': {
                        'Data': email_body
                    }
                }
            }
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Bug report with fix suggestions sent successfully!', 'response': response,'body':email_body})
        }

    except ClientError as e:
        print(f"Error sending email: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'Failed to send bug report with suggestions.', 'error': str(e)})
        }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'message': 'An unexpected error occurred.', 'error': str(e)})
        }

def get_fix_suggestions(bug_description):
    try:
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 500,
            "system": "Given the following bug description tell me a possible fix for this bug. Be verbose but don't try to be creative. Write one paragraph.",
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": bug_description}] 
                }
            ]
        }

        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response['body'].read().decode('utf-8'))

        print(response_body)

        if 'content' in response_body and isinstance(response_body['content'], list):
            if len(response_body['content']) > 0 and 'text' in response_body['content'][0]:
                return response_body['content'][0]['text'].strip()
            else:
                return "Text not found in the response."
        else:
            return "No 'content' key or invalid structure in response."

    except Exception as e:
        print(f"Error while getting fix suggestions: {e}")
        return f"Error occurred: {str(e)}"