import os
import json
import time
import boto3

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def handler(event, context):
    try:
        body = event["body"]

        chat_id = body["chat_id"]
        message = body["message"]
        timestamp = int(time.time())

        table.put_item(
            Item={
                "chat_id": str(chat_id),
                "timestamp": timestamp,
                "message": message
            }
        )

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Message saved successfully!"})
        }
    
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
