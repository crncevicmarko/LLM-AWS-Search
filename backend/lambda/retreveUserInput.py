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
    return results

# uses bedrock to generate embedding for user input text
def generate_text_embeding(user_input: str):
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

    return formatted_prompt 


def search_pinecone(query_vector):
    query_result = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True,
        namespace="jira"
    )
    
    result = parsResponse(query_result)
    return result

def generate_response_from_llm(prompt):
    response = bedrock_client.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1500,
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
    model_output = json.loads(response['body'].read().decode('utf-8'))
    return model_output.get('content')[0].get('text')

def format_prompt_for_llm(filtered_results, user_question, chat_history):
    if not filtered_results:
        # If no tickets are found, provide a useful alternative response
        return (
            f"Previous conversation: {chat_history}\n\n"
            f"The user asked: {user_question}. "
            f"Provide a **concise and relevant** response using key insights. "
            f"Offer guidance or suggest possible actions in 2-3 sentences max.\n\n"
            f"Assistant:"
        )

    formatted_results = []
    for match in filtered_results:
        title = match.get("text", "No Title Available")
        description = match.get("description", "No Description Available")
        url = match.get("ticket-url", "No ticket URL available")

        formatted_results.append(
            f"- **{title}**\n{description}\n({url})"
        )

    jira_ticket_results = "\n".join(formatted_results)

    return (
        f"Previous conversation: {chat_history}\n\n"
        f"The user asked: {user_question}. "
        f"Here is relevant information from the Jira tickets:\n\n"
        f"{jira_ticket_results}\n\n"
        f"Answer the question directly based on the ticket information. "
        f"Do **not** infer or provide additional details outside of the ticket descriptions. "
        f"Stick strictly to the content provided in the Jira tickets."
        f"Keep the response factual and concise.\n\n"
        f"Detect the language of the user's question and respond in the same language, ensuring that all parts of the response match the user's language. "
        f"Format the response like this:\n"
        f"- Start with a friendly introduction, showing enthusiasm and care for the user's request.\n"
        f"- List each relevant Jira ticket with:\n"
        f"  - Ticket Title\n"
        f"  - Descriptio(A summary of description of the ticket's purpose and tasks)\n"
        f"  - A URL to the ticket (this is the most important part and **must always be included**).\n"
        f"- Conclude with a warm, thoughtful closing statement that reassures the user, encourages further questions, and expresses eagerness to help. Example:\n"
        f"  'I hope this helps! If you need more details or have any follow-up questions, feel free to ask. I'm always here to assist you in navigating Jira and finding the right information. Let me know how I can help further!'"
        f"\nEnsure the response is structured, informative, and engaging. Every ticket must have a valid URL.\n"
        f"Assistant:"
    )

def process_chat_history(chat_history):
    """Keep the first 4 messages and summarize the rest if there are more."""
    
    if len(chat_history) > 4:
        first_four_messages = "\n".join(chat_history[:4])
        older_messages = "\n".join(chat_history[4:])

        summary_prompt = (
            f"Summarize the following chat history while keeping key details:\n\n{older_messages}"
        )
        summarized_history = generate_response_from_llm(summary_prompt)

        return first_four_messages + "\n" + summarized_history
    else:
        return "\n".join(chat_history)

def handler(event, context):
    try:
        body = json.loads(event.get("body","{}"))
        chat_history = body.get("chat_history", "")
        user_input = body.get("user_input", "")

        if not user_input:
            return{
                "statusCode":400,
                "body":json.dumps({"error":"No user input provided"})
            }
        
        chat_history = process_chat_history(chat_history)

        
        query_embedding = generate_text_embeding(chat_history + user_input)

        search_results = search_pinecone(query_embedding)

        prompt = format_prompt_for_llm(search_results, user_input, chat_history)

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
