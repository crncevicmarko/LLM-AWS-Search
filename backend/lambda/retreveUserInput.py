import json
import boto3

bedrock_client = boto3.client('bedrock-runtime', region_name="eu-west-1")

def handler(event, context):
    try:
        body = json.loads(event.get("body","{}"))
        message = body.get("text", "")
        print("Message: ", message)

        if not message:
            return{
                "statusCode":400,
                "body":json.dumps({"error":"No message provided"})
            }

        input_text={"inputText":message}

        response = bedrock_client.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            body=json.dumps(input_text),
            contentType="application/json",
            accept="application/json"
        )
        print("Response: ",str(response['body']))
        bedrock_response = json.loads(response['body'].read().decode('utf-8'))
        print("Bedrock Response: ",str(bedrock_response))
        model_output = bedrock_response.get("results")[0]["outputText"] # ("results") is list, so you need to iterate throught list and return every record not just first elemen(("results")[0])
        response = {
            "statusCode":200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, POST, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({"response": model_output})
        }
        return response
    
    except Exception as e:
        return {
            "statusCode":500,
            "body":json.dumps({"error":str(e)})
        }
