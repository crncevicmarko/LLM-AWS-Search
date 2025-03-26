import json


def handler(event, context):
    try:
        body = json.loads(event.get("body","{}"))
        message = body.get("message", "No message received")
        
        response = {
            "statusCode":200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"received": message})
        }
        return response
    
    except Exception as e:
        return {
            "statusCode":500,
            "body":json.dumps({"error":str(e)})
        }