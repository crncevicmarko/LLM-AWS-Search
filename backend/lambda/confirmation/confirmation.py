import json
import os
import boto3

cognito_client = boto3.client('cognito-idp')

def handler(event, context):
    try:
        body = json.loads(event['body'])
        username = body['username']
        confirmation_code = body['code']

      
        response = cognito_client.confirm_sign_up(
            ClientId=os.environ['CLIENT_ID'],  
            Username=username,
            ConfirmationCode=confirmation_code
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Email confirmed successfully'})
        }

    except Exception as e:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
