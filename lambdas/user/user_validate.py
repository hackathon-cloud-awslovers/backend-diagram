import boto3
from datetime import datetime
import json
import os

def load_body(event):
    if 'body' not in event:
        return event

    if isinstance(event["body"], dict):
        return event['body']
    else:
        return json.loads(event['body'])

def lambda_handler(event, context):
    """
    Lambda function to validate token.
    """

    print('Event:', event)

    body = load_body(event)

    token = body.get('token')
    tenant_id = body.get('tenant_id')

    if not token or not tenant_id:
        return {
            'statusCode': 403,
            'body': json.dumps('Missing token or tenant_id')
        }

    dynamodb = boto3.resource('dynamodb')
    table_auth_name = os.environ.get('TABLE_AUTH')
    table = dynamodb.Table(table_auth_name)

    response = table.get_item(
        Key={
            'token': token,
            'tenant_id': tenant_id
        }
    )

    if 'Item' not in response:
        print('Token not found:', token)
        return {
            'statusCode': 403,
            'body': json.dumps('Token no existe')
        }

    item = response['Item']

    # Extra check tenant_id
    if item.get('tenant_id') != tenant_id:
        print('Mismatch tenant_id:', item.get('tenant_id'))
        return {
            'statusCode': 403,
            'body': json.dumps('Token no corresponde al tenant')
        }

    expires = item.get('expires')
    print('Token expires at:', expires)

    # Current time in same format
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if now > expires:
        print('Token expired:', now)
        return {
            'statusCode': 403,
            'body': json.dumps('Token expirado')
        }

    print('Token válido')
    return {
        'statusCode': 200,
        'body': json.dumps('Token válido')
    }
