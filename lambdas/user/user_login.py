from datetime import datetime, timedelta

import boto3
import bcrypt
import os
import json
import secrets

# Expire time
expire_time = timedelta(hours=5)

# Hashear contraseña
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_token():
    return secrets.token_urlsafe(32)

def load_body(event):
    if 'body' not in event:
        return event

    if isinstance(event["body"], dict):
        return event['body']
    else:
        return json.loads(event['body'])

def lambda_handler(event, context):
    """
    Lambda function to handle user login.
    """
    table_auth_name = os.environ['TABLE_AUTH']
    table_user_name = os.environ['TABLE_USER']

    body = load_body(event)

    user_id = body.get('user_id')
    tenant_id = body.get('tenant_id')
    password = body.get('password')

    if not user_id or not tenant_id or not password:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: user_id, tenant_id, or password.'})
        }

    dynamodb = boto3.resource('dynamodb')
    table_user = dynamodb.Table(table_user_name)
    table_auth = dynamodb.Table(table_auth_name)

    # Retrieve user information
    response = table_user.get_item(
        Key={
            'tenant_id': tenant_id,
            'user_id': user_id
        }
    )
    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'User not found.'})
        }

    db_password = response['Item'].get('password')

    # La verificación estaba al revés
    if not verify_password(password, db_password):
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Wrong password.'})
        }

    # Create an auth token
    token = generate_token()
    expiration_time = (datetime.now() + expire_time).isoformat()

    table_auth.put_item(
        Item={
            'token': token,
            'tenant_id': tenant_id,
            'user_id': user_id,
            'expires_at': expiration_time
        }
    )

    # Devolver token en body + header
    return {
        'statusCode': 200,
        'body':{
            'token': token,
            'expires_at': expiration_time
        },
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    }
