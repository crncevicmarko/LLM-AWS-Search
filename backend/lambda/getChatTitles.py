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
        logger.info(f"Querying title for chat_id: {chat_id}")

        # Perform the query to retrieve the chat details (assuming 'title' is stored)
        response = table.query(
            KeyConditionExpression="chat_id = :chat_id",
            ExpressionAttributeValues={":chat_id": chat_id}
        )

        # Extract the chat details from the response
        items = response.get("Items", [])

        # If no items are found, return a not found message
        if not items:
            logger.warn(f"No chat found for chat_id: {chat_id}")
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Chat not found"})






            }

        # Assuming the first item contains the chat details and it has a 'title' attribute
        chat_title = items[0].get('title', 'No title available')

        # Log the retrieved title
        logger.info(f"Retrieved chat title for chat_id: {chat_id}: {chat_title}")

        # Return the title in the response
        return {
            "statusCode": 200,
            "body": json.dumps({"chat_id": chat_id, "title": chat_title})
        }

    except Exception as e:
        logger.exception("Error querying DynamoDB")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
