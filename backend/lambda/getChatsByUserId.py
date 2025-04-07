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
    user_id = query_params.get("user_id") if query_params else None

    if not user_id:
        logger.warning("Missing user_id parameter in request.")
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing user_id parameter"})
        }

    table = dynamodb.Table(TABLE_NAME)

    try:
        logger.info(f"Querying chats for user_id: {user_id}")
        response = table.scan(
            FilterExpression="user_id = :user_id",
            ExpressionAttributeValues={":user_id": user_id}
        )

        chats = response.get("Items", [])
        logger.info(f"Retrieved {len(chats)} chats for user_id: {user_id}")

        return {
            "statusCode": 200,
            "body": json.dumps({"chats": chats})
        }

    except Exception as e:
        logger.exception("Error querying DynamoDB")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
