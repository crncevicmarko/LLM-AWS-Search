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
        # Create the payload based on the required structure
        body = {
            "modelId": "amazon.nova-micro-v1:0",
            "contentType": "application/json",
            "accept": "application/json",
            "body": {
                "inferenceConfig": {
                    "max_new_tokens": 50  # Set max tokens as desired
                },
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
        }

        # Make the API request to invoke the model
        response = bedrock_client.invoke_model(
            modelId=body["modelId"],
            body=json.dumps(body["body"]),  # Send the body content as JSON
            accept=body["accept"],
            contentType=body["contentType"]
        )

        # Parse the model's response
        response_body = json.loads(response['body'].read().decode('utf-8'))

        # Check if the response contains choices and extract the message content
        if 'choices' in response_body:
            choices = response_body['choices']
            if choices:
                return choices[0].get('text', 'No response')
        return 'No choices in response'

    except Exception as e:
        return f"Error generating response: {str(e)}"

def generate_title(prompt):
    """Generate a concise title for the conversation."""
    title_prompt = f"Generate a short and relevant title for this conversation:\n\n{prompt}"
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
