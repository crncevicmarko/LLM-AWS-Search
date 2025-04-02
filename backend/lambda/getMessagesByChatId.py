import json
import boto3
import os

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]

def handler(event, context):
    
    query_params = event.get("queryStringParameters", {})
    chat_id = query_params.get("chat_id") if query_params else None
    
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

        return {
            "statusCode": 200,
            "body": json.dumps({"messages": messages})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
