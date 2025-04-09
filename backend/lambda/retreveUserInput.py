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
        print("29 : ",metadata)
        print("Score : ",match.get("score"))
        if match.get("score") >= 0.01:
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

def format_prompt_for_llm(filtered_results, user_question, chat_history):
    print("Entered format_prompt_for_llm", filtered_results)

    if not filtered_results:
        # If no tickets are found, provide a useful alternative response
        return generate_unknown_prompt(user_question, chat_history)

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
        f"Always respond in English, regardless of the user's input language. "
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
    
def format_chat_history_for_llm(chat_history, max_keep=4):
    """
    Process chat history for the LLM:
    - Keep the first `max_keep` messages as-is
    - Summarize older messages
    - Return a list of structured messages (role/content)
    """
    # user_input = input_data.get("user_input", "")
    messages = []

    if len(chat_history) > max_keep:
        first_messages = chat_history[:max_keep]
        older_messages = chat_history[max_keep:]

        summary_prompt = (
            f"Summarize the following chat history, keeping important details clear and concise:\n\n"
            + "\n".join([f"User: {msg['user_message']} | Assistant: {msg['chat_message']}" for msg in older_messages])
        )
        summarized_history = generate_response_from_llm(summary_prompt)

        messages.append({
            "role": "system",
            "content": f"Previous conversation summary: {summarized_history}"
        })

        for msg in first_messages:
            messages.append({
                "role": "user",
                "content": msg["user_message"]
            })
            messages.append({
                "role": "assistant",
                "content": msg["chat_message"]
            })
    else:
        for msg in chat_history:
            messages.append({
                "role": "user",
                "content": msg["user_message"]
            })
            messages.append({
                "role": "assistant",
                "content": msg["chat_message"]
            })

    # User input will be formatted in prompt separately from chat history
    # if user_input:
    #     messages.append({
    #         "role": "user",
    #         "content": user_input
    #     })

    message_string = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
    print(f"CHAT HISTORY STRING: {message_string}")
    return message_string
    
def generate_unknown_prompt(user_input, chat_history):
    if not chat_history:
        chat_history = "No previous conversation available."
    return (
        f"Previous conversation:\n{chat_history}\n\n"
        f"User's latest message: {user_input}\n\n"
        "Please continue the conversation naturally based on the above. "
        "Older messages are provided for background but are less important. "
        "Respond directly to the user without explaining that you are continuing the conversation. "
        "Be friendly, helpful, and concise."
    )

def handler(event, context):
    try:
        body = json.loads(event.get("body","{}"))
        user_input = body.get("user_input", "")
        chat_history = body.get("chat_history", [])
      
        if not user_input:
            return{
                "statusCode":400,
                "body":json.dumps({"error":"Nso user input provided"})
            }

        formatted_chat_history = format_chat_history_for_llm(chat_history)
        #MAIN AGENT
        search_results=main_agent(user_input,formatted_chat_history)

        print(search_results)
        if(search_results[0].get("text") == "Unknown"):
            prompt = generate_unknown_prompt(user_input, chat_history)
        else:
            prompt = format_prompt_for_llm(search_results, user_input, formatted_chat_history)

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

def intent_classifier(user_input):
    prompt= ("You are an assistant that helps classify user requests into categories.\n"
            f"""Classify the following user query into one of these categories: "metadata", "description", or "unknown".\n"""
            f"User query: {user_input}\n"
            'First, check if the query is related to technology, software development, AWS services, Angular, programming, or IT systems.'
            'If the query is not related to any of these, classify it as "unknown"'
            'If the query is related to any of these, classify it as one of metadata or description using following categories'
            f"""- "metadata" for queries asking for creator, assignee, or mentioning keywords such as (creator, assignee, id, created by, assigned to, creator's name, created on, reporter, owner)
            - "description" for questions regarding the main content of the ticket or containing keywords such as (how, summary, did, what, task, issue, problem, action, steps, work, description)
            - "unknown" for any other queries, including those that are not related to technical topics, AWS services, Angular, or software development in general.\n"""
            'For example output should be in this format: <category_name>'
            )
    try:
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
    except Exception as e:
        return f"Error classifying input:  {e}"

def search_pinecone_metadata(query_vector, params):
    ticket_id = params.get('id', None)
    creator_name = params.get('creator', None)
    # assignee=params.get('assignee',None)
    filter_conditions = {}
    if ticket_id:
        filter_conditions["id"] = {"$eq": ticket_id}
    if creator_name:
        filter_conditions["creator"] = {"$eq": creator_name}

    query_result = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True,
        filter=filter_conditions, 
        namespace="jira"
    )

    print("Creator name : "+creator_name)

    result = parsResponse(query_result)
    return result

def search_pinecone_description(query_vector):
 
    query_result = index.query(
        vector=query_vector,
        top_k=5,
        include_metadata=True,
        filter=None, 
        namespace="jira"
    )

    result = parsResponse(query_result)
    return result

def main_agent(user_input, chat_history):
    category = intent_classifier(user_input).lower()
    query_embedding = generate_text_embeding(chat_history + user_input)

    print(f"[main_agent] Intent category: {category}")

    if "metadata" in categorys:
        print("316: "+ user_input)
        prompt_for_pinecone_query = format_prompt_for_pinecone(user_input)
        print("317 "+prompt_for_pinecone_query)
        params_response = generate_response_from_llm(prompt_for_pinecone_query)
        print("319 ",params_response)
        
        try:
            extracted_params = json.loads(params_response)
        except json.JSONDecodeError:
            print("[main_agent] JSON parsing error from LLM response:", params_response)
            extracted_params = {}

        print(f"[main_agent] Extracted metadata params: {extracted_params}")
        return search_pinecone_metadata(query_embedding, extracted_params)

    elif "description" in category:
        return search_pinecone_description(query_embedding)

    else :  # unknown
    #     def parsResponse(query_result: str):
    # results = []
    # for match in query_result.get("matches", []):
    #     metadata = match.get("metadata", {})
    #     print("29 : ",metadata)
    #     print("Score : ",match.get("score"))
    #     if match.get("score") >= 0.01:
    #         results.append({
    #             "score": match.get("score"),
    #             "text": metadata.get("text"),
    #             "ticket-url": metadata.get("ticket-url"),
    #         })
    # return 
        results_unknown = []
        results_unknown.append({
            "score": None,
            "text": "Unknown",
            "ticket-url": None
        })
        return results_unknown

# def main_agent(user_input,chat_history):
#     category=intent_classifier(user_input)
#     query_embedding = generate_text_embeding(chat_history + user_input)#SVAKAKO TREBA
#   #------------------------------------------------------------------------
#     prompt_for_pinecone = format_prompt_for_pinecone(user_input)
        
#         # {
#         #     id: "SCRUM-1",
#         #     creator: "VESNA"
#         # } U SEARCH PARAMS
#     search_params = generate_response_from_llm(prompt_for_pinecone)
#     if(category=="metadata"):
#         return search_pinecone_metadata(query_embedding,search_params)
#     elif(category=="description"):
#         return search_pinecone_description(query_embedding)
#     else:
#         return unknown_response(user_input)