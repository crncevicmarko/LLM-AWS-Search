import json
import os
import secrets
import boto3
bedrock_client = boto3.client('bedrock-runtime', region_name="eu-west-1")

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["TABLE_NAME"])


def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return secret

def generate_response_from_llm(prompt):
    model_id = "arn:aws:bedrock:eu-west-1:785202558517:inference-profile/eu.anthropic.claude-3-7-sonnet-20250219-v1:0"
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "top_k": 150,
        "stop_sequences": [],
        "temperature": 1,
        "top_p": 0.999,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
    }
    response = bedrock_client.invoke_model(
        modelId=model_id,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json"
    )
    model_output = json.loads(response['body'].read().decode('utf-8'))
    return model_output.get('content')[0].get('text')

def generate_title(prompt):
   
    title_prompt = f"Generate a short and relevant title based on this question.\n{prompt}"
    title = generate_response_from_llm(title_prompt)
    return title.strip()  # Strip any unnecessary whitespace


def handler(event, context):

    try:
        body = json.loads(event["body"])
        chat_id = body["chat_id"]
        user_id = body["user_id"]
        valueToUser=generate_title(body.get('text'))
        table.put_item(
            Item={
                "chat_id": str(chat_id),
                "title":valueToUser,
                "user_id":str(user_id)
            }
        )

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
