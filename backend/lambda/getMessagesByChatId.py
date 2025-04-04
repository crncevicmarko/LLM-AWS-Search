import json
import boto3
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource("dynamodb")
TABLE_NAME = os.environ["TABLE_NAME"]

def handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    
    query_params = event.get("queryStringParameters", {})
    chat_id = query_params.get("chat_id") if query_params else None
    
    if not chat_id:
        logger.warning("Missing chat_id parameter in request.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing chat_id parameter"})
        }

    table = dynamodb.Table(TABLE_NAME)

    try:
        logger.info(f"Querying messages for chat_id: {chat_id}")
        response = table.query(
            KeyConditionExpression="chat_id = :chat_id",
            ExpressionAttributeValues={":chat_id": chat_id}
        )
        messages = response.get("Items", [])
        logger.info(f"Retrieved {len(messages)} messages for chat_id: {chat_id}")

        return {
            "statusCode": 200,
            "body": json.dumps({"messages": messages})
        }

    except Exception as e:
        logger.exception("Error querying DynamoDB")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
