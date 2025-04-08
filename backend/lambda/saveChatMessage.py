import os
import json
import time
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def handler(event, context):
    try:
        body = json.loads(event.get("body","{}"))

        user_id = body.get("user_id", "")
        chat_id = body.get("chat_id", "")
        userMessage = body.get("user_message","")
        chatMessage = body.get("chat_message","")
        timestamp = int(time.time())

        table.put_item(
            Item={
                "user_id": str(user_id),
                "chat_id": str(chat_id),
                "timestamp": timestamp,
                "user_message": userMessage,
                "chat_message": chatMessage,
            }
        )

        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, POST, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({"message": "Message saved successfully!"})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
