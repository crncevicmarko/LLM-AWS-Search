import json
import os
import secrets
import boto3
from pinecone import Pinecone

bedrock_client = boto3.client('bedrock-runtime', region_name="eu-west-1")

# Set up Pinecone client 10-23 line
def get_secret(secret_arn):
    client = boto3.client("secretsmanager")
    response = client.get_secret_value(SecretId=secret_arn)
    secret = json.loads(response["SecretString"])
    return secret

secret_arn = os.getenv("PINECONE_SECRET_ARN")
secrets = get_secret(secret_arn)

PINECONE_API_KEY = secrets["apiKey"]
PINECONE_INDEX_NAME = secrets["indexUrl"]

pc = Pinecone(api_key=PINECONE_API_KEY, environment="us-east-1")
index = pc.Index(host=PINECONE_INDEX_NAME)

def parsResponse(query_result: str):
    results = []
    for match in query_result.get("matches", []):
        metadata = match.get("metadata", {})

        if match.get("score") >= 0.25:
            results.append({
                "score": match.get("score"),
                "text": metadata.get("text"),
                "ticket-url": metadata.get("ticket-url"),
            })
    print("Query result: ", results)
    return results



# uses bedrock to generate embedding for user input text
def generate_text_embeding(user_input: str):
    print("User input: ",user_input)
    input_text={"inputText":user_input}
    response=bedrock_client.invoke_model(
        modelId="amazon.titan-embed-text-v2:0",
        body=json.dumps(input_text),
        accept="application/json",
        contentType="application/json"
    )   
    model_output = json.loads(response["body"].read())["embedding"]
    return model_output


def search_pinecone(query_vector):
    query_result = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True,
        namespace="jira"
    )

    print("Query result: ", query_result)
    
    result = parsResponse(query_result)
    return result

def generate_response_from_llm(prompt):
    response = bedrock_client.invoke_model(
        modelId="amazon.titan-text-lite-v1",
        body=json.dumps({"inputText": prompt}),
        accept="application/json",
        contentType="application/json"
    )
    model_output = json.loads(response['body'].read().decode('utf-8'))
    print("Model output1: ", model_output)
    print("Model output2: ", model_output.get("results")[0]["outputText"])
    return model_output.get("results")[0]["outputText"] # list iteriraj

def format_prompt_for_llm(filtered_results):
    print("Entered format_prompt_for_llm")
    
    if not filtered_results:
        return "There are no relevant tickets found for the given query."
    print("After filtered_results")

    prompt = "Based on the following ticket information, generate a helpful response for the user and display the url for every ticket information:\n\n"
    print("After prompt")
    for match in filtered_results:
        title = match.get('text', 'No Title Available')
        description = match.get('description', 'No Description Available')
        url = match.get('ticket-url', 'No ticket URL available')
        
        prompt += f"**Ticket Title:** {title}\n"
        prompt += f"**Description:** {description}\n"
        prompt += f"**Ticket URL:** {url}\n\n"
    print("After for loop")
    prompt += "Make the structured response where are you going to return the Ticket Title, summarized Description and URL to that ticket that you are describing"
    print("After prompt +=")
    return prompt

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
        
        query_embedding = generate_text_embeding(message)

        search_results = search_pinecone(query_embedding)
        print("Search results: ", search_results)

        # prompt = format_prompt_for_llm(search_results)
        # print("Prompt: ", prompt)

        # valueToUser = generate_response_from_llm(prompt)
        # print("Value to user: ", valueToUser)

        return {
            "statusCode":200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, POST, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({"response": search_results})
        }
    
    except Exception as e:
        return {
            "statusCode":500,
            "body":json.dumps({"error":str(e)})
        }
