import json
import os
import boto3
import pinecone


def mock_bedrock(prompt):
    
    # bedrock = boto3.client('bedrock-runtime',region_name="eu-west-1")
    # response = bedrock.invoke_model(
    #     modelId='amazon.titan-embed-text-v1',
    #     body=json.dumps({'inputText': prompt})
    # )
    # return json.loads(response['body'].read())

    """Simulate Titan LLM response without real AWS calls"""
    return {
        "response": f"I found these Jira tickets related to '{prompt}': [SCRUM-123, SCRUM-456]",
        "embedding": [0.1, 0.2, ...]
    }

def mock_pinecone(query_embedding, top_k=3):
    # pinecone.init(api_key=os.environ['PINECONE_KEY'])
    # index = pinecone.Index('ime-indeksa')
    # return index.query(vector=embedding, top_k=3)
    #vrati top 3 rezultata (tiketa) koji su najrelevantniji
    """Simulate Pinecone query without real DB calls"""
    return {
        "matches": [
            {
                "id": "SCRUM-123",
                "metadata": {
                    "title": "Login page bug",
                    "url": "https://jira/SCRUM-123"
                }
            }
        ]
    }

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        prompt = body['prompt']
    except:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid request format'})
        }
    
    
    llm_response = mock_bedrock(prompt)
    
    pinecone_results = mock_pinecone(llm_response['embedding'])
    
    response = {
        "answer": llm_response['response'],
        "tickets": [
            {
                "key": match['id'],
                "title": match['metadata']['title'],
                "url": match['metadata']['url']
            }
            for match in pinecone_results['matches']
        ]
    }
    
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(response)
    }