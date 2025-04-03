import json
import os
import secrets
import boto3
bedrock_client = boto3.client('bedrock-runtime', region_name="eu-west-1")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ChatHistory')  # Use your DynamoDB table name


def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return secret


def generate_response_from_llm(prompt):
    try:
       
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 50,  # Adjust as needed
            "messages": [
                {
                    "role": "user",
                    "content": [{"type": "text", "text": prompt}]  # Haiku requires "type" and "text"
                }
            ]
        }

        response = bedrock_client.invoke_model(
            modelId="anthropic.claude-3-haiku-20240307-v1:0",  # Haiku model ID
            body=json.dumps(request_body),
            accept="application/json",
            contentType="application/json"
        )

        response_body = json.loads(response['body'].read().decode('utf-8'))
        
        # Extract response from Haiku's structure
        if 'content' in response_body:
            return response_body['content'][0]['text'].strip()
        return "No response generated"

    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_title(prompt):
   
    title_prompt = f"Generate a short and relevant title based on this question. Don't answer the question just give me back the title with fewest words possible:\n\n{prompt}"
    title = generate_response_from_llm(title_prompt)
    return title.strip()  # Strip any unnecessary whitespace


def handler(event, context):
    try:
        body = json.loads(event.get("body", ""))

        valueToUser=generate_response_from_llm(body.get('text'))

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, POST, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({"response": valueToUser})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
