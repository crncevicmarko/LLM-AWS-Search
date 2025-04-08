import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]

def convert_decimal(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    elif isinstance(obj, list):
        return [convert_decimal(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimal(value) for key, value in obj.items()}
    return obj


def handler(event, context):
    
    query_params = event.get("queryStringParameters", {})
    chat_id = query_params.get("chat_id") if query_params else None
    print(f"Query parameters: {query_params}")
    print(f"Chat ID: {chat_id}")
    if not chat_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing chat_id parameter"})
        }

    table = dynamodb.Table(TABLE_NAME)

    try:
        response = table.query(
            KeyConditionExpression="chat_id = :chat_id",
            ExpressionAttributeValues={":chat_id": chat_id}
        )
        messages = response.get("Items", [])
        messages = convert_decimal(messages)

        print(f"Query result: {messages}")

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, POST, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({"messages": messages})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
