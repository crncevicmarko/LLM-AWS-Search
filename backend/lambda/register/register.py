import json
import os
import boto3


cognito_client=boto3.client('cognito-idp')

def handler(event,context):
    try:
        body=json.loads(event['body'])
        username=body['username']
        password=body['password']
        email=body['email']
        name=body['firstname']
        surname=body['surname']

        response = cognito_client.sign_up(
            ClientId=os.environ['CLIENT_ID'],  
            Username=username,
            Password=password,
            UserAttributes=[
               {'Name': 'email', 'Value': email},
                {'Name': 'given_name', 'Value': name},
                {'Name': 'family_name', 'Value': surname}
            ]
        )


        return {
            'statusCode': 200,
            'body': json.dumps("Registration successful. Please check your email to confirm."),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': "POST, OPTIONS",
                'Access-Control-Allow-Credentials': 'true'
            }
        }

    except Exception as e:
        
        return {
            'statusCode': 400,
            'body': json.dumps(f"Error: {str(e)}"),
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': "POST, OPTIONS",
                'Access-Control-Allow-Credentials': 'true'
            }
        }
