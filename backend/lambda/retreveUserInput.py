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
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_URL")

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

def loadTheTxt(filter_results, user_question):
    with open("prompts/chat_prompt.txt", "r") as txt_file:
        template = txt_file.read()  # Read file content

    formatted_prompt = template.format(results=filter_results, question=user_question)

    print("Txt File: ", formatted_prompt)

    return formatted_prompt 


def search_pinecone(query_vector, params):
    ticket_id = params.get('id', None)
    creator_name = params.get('creator', None)

    filter_conditions = {}
    if ticket_id:
        filter_conditions["id"] = {"$eq": ticket_id}
    if creator_name:
        filter_conditions["creator"] = {"$eq": creator_name}

    query_result = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True,
        filter=filter_conditions if filter_conditions else None, 
        namespace="jira"
    )

    print("Query result: ", query_result)
    
    result = parsResponse(query_result)
    return result

def generate_response_from_llm(prompt):
    print("Entered generate_response_from_llm1: ", prompt)
    response = bedrock_client.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ]
            }
        ),
        accept="application/json",
        contentType="application/json"
    )
    print("Response1: ", response)
    model_output = json.loads(response['body'].read().decode('utf-8'))
    print("Model output1: ", model_output)
    print("Model output2: ", model_output.get('content')[0].get('text'))
    return model_output.get('content')[0].get('text')

def format_prompt_for_pinecone(user_question):
    prompt = (f"Extract specific information from the following text. If the text contains any mention of a creator (such as 'creator', 'created by', 'author', or similar terms), extract the name following that mention and assign it to the 'creator' field in a JSON object."
    f"If the text includes an ID in the format 'SCRUM-' followed by a number (e.g., SCRUM-12), extract it and assign it to the 'id' field."
    f"If neither of these values is found, return an empty JSON."
    f"Input text: {user_question}"
    f"Output Format: The output **must** be **valid JSON only**, without any additional text."
    """{
    "creator": '<extracted_creator_name>',
    "id": '<extracted_id>'
    }"""
    "If no relevant information is found, return: {} and if only one relevant information is found return only one"
    )
    return prompt

def format_prompt_for_llm(filtered_results, user_question):
    print("Entered format_prompt_for_llm", filtered_results)

    if not filtered_results:
        return "There are no relevant tickets found for the given query."

    formatted_results = []
    for match in filtered_results:
        title = match.get("text", "No Title Available")
        description = match.get("description", "No Description Available")
        url = match.get("ticket-url", "No ticket URL available")

        formatted_results.append(
            f"- **Ticket Title**: {title}\n"
            f"  **Description**: {description}\n"
            f"  **URL**: {url}"
        )

    results_str = "\n".join(formatted_results)

    prompt = (
        f"Human: You are a helpful and enthusiastic assistant who provides clear, structured, and detailed answers. "
        f"Based on the provided Jira ticket results, answer the user's question in an engaging and caring way. "
        f"Results: {results_str} "
        f"User question: {user_question} "
        f"Format the response like this:\n"
        f"- Start with a friendly introduction, showing enthusiasm and care for the user's request.\n"
        f"- List each relevant Jira ticket with:\n"
        f"  - Ticket Title\n"
        f"  - Descriptio(A summary of description of the ticket's purpose and tasks)\n"
        f"  - A URL to the ticket (this is the most important part and **must always be included**).\n"
        f"- Conclude with a warm, thoughtful closing statement that reassures the user, encourages further questions, and expresses eagerness to help. Example:\n"
        f"  'I hope this helps! If you need more details or have any follow-up questions, feel free to ask. I'm always here to assist you in navigating Jira and finding the right information. Let me know how I can help further!'"
        f"\nEnsure the response is structured, informative, and engaging. **Every ticket must have a valid URL.**\n"
        f"Assistant:"
    )


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

        prompt_for_pinecone = format_prompt_for_pinecone(message)
        search_params = generate_response_from_llm(prompt_for_pinecone)

        # print(f"Search params: {search_params}")

        search_results = search_pinecone(query_embedding, json.loads(search_params))
        print("Search results: ", search_results)

        prompt = format_prompt_for_llm(search_results, message)
        print("Prompt2: ", prompt)

        valueToUser = ""
        if not prompt or "there are no relevant tickets found for the given query" in prompt.lower():
            valueToUser = "There are no relevant tickets for the given request."
        else:
            valueToUser = generate_response_from_llm(prompt)

        return {
            "statusCode":200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "OPTIONS, POST, GET",
                "Access-Control-Allow-Headers": "Content-Type, Authorization"
            },
            "body": json.dumps({"response": valueToUser})
        }
    
    except Exception as e:
        return {
            "statusCode":500,
            "body":json.dumps({"error":str(e)})
        }
