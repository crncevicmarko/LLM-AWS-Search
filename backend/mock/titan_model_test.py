import boto3
import json
import pprint

client = boto3.client(service_name='bedrock-runtime', region_name="eu-west-1")

titan_model_id = "amazon.titan-text-lite-v1"
prompt = input("Input prompt: ")

titan_config = json.dumps({
            "inputText": prompt,
            "textGenerationConfig": {
                "maxTokenCount": 4096,
                "stopSequences": [],
                "temperature": 0,
                "topP": 0.9
            }
        })

response = client.invoke_model(
    body=titan_config,
    modelId=titan_model_id,
    accept="application/json",
    contentType="application/json"
)

response_body = json.loads(response.get('body').read())

pp = pprint.PrettyPrinter(depth=4)

pp.pprint(response_body.get('results'))