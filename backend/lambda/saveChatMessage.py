import os
import json
import time
import boto3
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(os.environ["TABLE_NAME"])

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")

    try:
        body = event["body"]

        chat_id = body["chat_id"]
        message = body["message"]
        timestamp = int(time.time())

        logger.info(f"Saving message for chat_id: {chat_id} at timestamp: {timestamp}")

        table.put_item(
            Item={
                "chat_id": str(chat_id),
                "timestamp": timestamp,
                "message": message
            }
        )

        logger.info("Message saved successfully.")

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Message saved successfully!"})
        }
    
    except Exception as e:
        logger.exception("Error saving message to DynamoDB.")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
