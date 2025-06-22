from datetime import timedelta

import boto3
import bcrypt
import os
import json

# Expire time
expire_time = timedelta(hours=5)

def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def lambda_handler(event, context):
    table_auth_name = os.environ['TABLE_AUTH']
    table_user_name = os.environ['TABLE_USER']

    body = json.loads(event.get('body', '{}'))

    user_id = body.get('user_id')
    tenant_id = body.get('tenant_id')
    password = body.get('password')
    if not user_id or not tenant_id or not password:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: user_id, tenant_id, or password.'
        }

    dynamodb = boto3.resource('dynamodb')
    table_user = dynamodb.Table(table_user_name)
    table_auth = dynamodb.Table(table_auth_name)

    # Check if user already exists
    response = table_user.get_item(
        Key={
            'tenant_id': tenant_id,
            'user_id': user_id
        }
    )
    if 'Item' in response:
        return {
            'statusCode': 400,
            'body': 'User already exists.'
        }

    # Hash the password
    hashed_password = hash_password(password)
    # Register the user
    table_user.put_item(
        Item={
            'tenant_id': tenant_id,
            'user_id': user_id,
            'password': hashed_password
        }
    )

    # Create an auth token
    token = bcrypt.gensalt().decode()
    # Store the auth token
    table_auth.put_item(
        Item={
            'token': token,
            'tenant_id': tenant_id,
            'user_id': user_id,
            'expire_time': (context.get_remaining_time_in_millis() + expire_time.total_seconds() * 1000)
        }
    )

    # Return success response
    return {
        'statusCode': 200,
        'body': 'User registered successfully.'
    }
