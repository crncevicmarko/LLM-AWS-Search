import json
import os
import secrets
import boto3
from pinecone import Pinecone

bedrock_client = boto3.client('bedrock-runtime', region_name="eu-west-1")

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
        print("Score : ",match.get("score"))
        if match.get("score") >= 0.01:
            results.append({
                "score": match.get("score"),
                "text": metadata.get("text"),
                "creator": metadata.get("creator"),
                "assignee": metadata.get("assignee"),
                "status": metadata.get("status"),
                "time_created": metadata.get("time-created"),
                "time_updated": metadata.get("time-updated"),
                "ticket-url": metadata.get("ticket-url"),
            })
    return results

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
        template = txt_file.read()  

    formatted_prompt = template.format(results=filter_results, question=user_question)

    return formatted_prompt 

def generate_response_from_llm(prompt):
    model_id = "arn:aws:bedrock:eu-west-1:785202558517:inference-profile/eu.anthropic.claude-3-7-sonnet-20250219-v1:0"
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 1500,
        "top_k": 150,
        "stop_sequences": [],
        "temperature": 1,
        "top_p": 0.999,
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
    response = bedrock_client.invoke_model(
        modelId=model_id,
        body=json.dumps(payload),
        contentType="application/json",
        accept="application/json"
    )
    model_output = json.loads(response['body'].read().decode('utf-8'))
    return model_output.get('content')[0].get('text')

def format_prompt_for_pinecone(user_question):
    prompt = (f"Extract specific information from the following text. If the text contains any mention of a creator (such as 'creator', 'created by', 'author', or similar terms), extract the name following that mention and assign it to the 'creator' field in a JSON object."
    f"If the text contains any mention of a assignee (such as 'assignee', 'assigned on', or similar terms), extract the name following that mention and assign it to the 'assignee' field in a JSON object."
    f"If the text includes status in the format 'Done', 'In Progress', 'To Do', extract it and assign it to the 'status' field"
    f"If the text includes time created (e.g., time when ticket created) in the format of date, extract it and assign it to the 'time_created' field"
    f"If the text includes time updated (e.g., time when ticket updated) in the format of date, extract it and assign it to the 'time_created' field"
    f"If the text includes an ID in the format 'SCRUM-' followed by a number (e.g., SCRUM-12), extract it and assign it to the 'id' field."
    f"If neither of these values is found, return an empty JSON."
    f"Input text: {user_question}"
    f"Output Format: The output **must** be **valid JSON only**, without any additional text."
    """{
    "creator": '<extracted_creator_name>',
    "assignee": '<extracted_assignee_name>',
    "status" : '<extracted_status>',
    "time_created": '<extracted_time_created>',
    "time_updated": 'extracted_time_updated>',
    "id": '<extracted_id>'
    }"""
    "If no relevant information is found, return: {} and if only one relevant information is found return only one"
    )
    return prompt

def format_prompt_for_llm(filtered_results, user_question, chat_history):

    if not filtered_results:
        return generate_unknown_prompt(user_question, chat_history)

    formatted_results = []
    for match in filtered_results:
        print(match)
        title = match.get("text", "No Title Available")
        description = match.get("description", "No Description Available")
        url = match.get("ticket-url", "No ticket URL available")
        creator = match.get("creator", "No creator available")
        assignee = match.get("assignee", "No assignee available")
        status = match.get("status", "No status available")
        time_created = match.get("time_created", "")
        time_updated = match.get("time_updated", "")

        formatted_results.append(
            f"- **{title}**\n{description}\nCreator: {creator}, Assignee: {assignee}, Status: {status},"
            f"Time Created: {time_created}, Time Updated: {time_updated}({url})"
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
        f"Format the response like this:\n"
        f"- List each relevant Jira ticket with:\n"
        f"  - Ticket Title\n"
        f"  - Description(A summary of description of the ticket's purpose and tasks)\n"
        f"  - Creator, Assignee, Status"
        f"  - Time Created, Time Updated"
        f"  - A URL to the ticket (this is the most important part and **must always be included**).\n"
        f"- Conclude with a warm, thoughtful closing statement that reassures the user, encourages further questions, and expresses eagerness to help. Example:\n"
        f"  'I hope this helps! If you need more details or have any follow-up questions, feel free to ask. I'm always here to assist you in navigating Jira and finding the right information. Let me know how I can help further!'"
        f"\nEnsure the response is structured, informative, and engaging. Every ticket must have a valid URL.\n"
    )
    
def format_chat_history_for_llm(chat_history, max_keep=4):
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

    message_string = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
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

        if(search_results and search_results[0].get("text") == "Unknown"):
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
            'First, check if the query is related to technology, software development, AWS services, Angular, programming,Jira , Pinecone , Bedrock or IT systems.'
            'If the query is not related to any of these, classify it as "unknown"'
            'If the query is related to any of these, classify it as one of metadata or description using following categories'
            f"""- "metadata" for queries asking for creator, assignee, or mentioning keywords such as (creator, assignee, id, created by, assigned to, creator's name, created on, reporter, owner)
            - "description" for questions regarding the main content of the ticket or containing keywords such as (how, summary, did, what, task, issue, problem, action, steps, work, description)
            - "unknown" for any other queries, including those that are not related to technical topics, AWS services, Angular, or software development in general.\n"""
            'For example output should be in this format: <category_name>'
            )
    try:
        return generate_response_from_llm(prompt)
    except Exception as e:
        return f"Error classifying input:  {e}"

def search_pinecone_metadata(query_vector, params):
    ticket_id = params.get('id', None)
    creator_name = params.get('creator', None)
    status = params.get('status', None)
    assignee = params.get('assignee', None)
    time_created = params.get('time_created', None)
    time_updated = params.get('time_updated', None)

    filter_conditions = {}
    if ticket_id:
        filter_conditions["id"] = {"$eq": ticket_id.lower()}
    if creator_name:
        filter_conditions["creator"] = {"$eq": creator_name.lower()}
    if assignee:
        filter_conditions["assignee"] = {"$eq": assignee.lower()}
    if status:
        filter_conditions["status"] = {"$eq": status.lower()}
    if time_created:
        filter_conditions["time_created"] = {"$eq": time_created}
    if time_updated:
        filter_conditions["time_updated"] = {"$eq": time_updated}
    print(filter_conditions)
    query_result = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True,
        filter=filter_conditions, 
        namespace="jira"
    )

    result = parsResponse(query_result)
    return result

def search_pinecone_description(query_vector):
 
    query_result = index.query(
        vector=query_vector,
        top_k=3,
        include_metadata=True,
        filter=None, 
        namespace="jira"
    )

    result = parsResponse(query_result)
    return result

def main_agent(user_input, chat_history):
    category = intent_classifier(user_input).lower()
    query_embedding = generate_text_embeding(user_input.lower())

    print(f"[main_agent] Intent category: {category}")

    if "metadata" in category:
        prompt_for_pinecone_query = format_prompt_for_pinecone(user_input)
        params_response = generate_response_from_llm(prompt_for_pinecone_query)
        print(params_response)
        
        try:
            extracted_params = json.loads(params_response)
        except json.JSONDecodeError:
            extracted_params = {}
        
        return search_pinecone_metadata(query_embedding, extracted_params)

    elif "description" in category:
        return search_pinecone_description(query_embedding)

    else :
        results_unknown = []
        results_unknown.append({
            "score": None,
            "text": "Unknown",
            "ticket-url": None
        })
        return results_unknown
