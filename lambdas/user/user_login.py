
from datetime import datetime, timedelta

import boto3
import bcrypt
import os

# Expire time
expire_time = timedelta(hours=5)

# Hashear contraseña
def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode(), hashed.encode())


def lambda_handler(event, context):
    """
    Lambda function to handle user login.
    """
    table_auth_name = os.environ['TABLE_AUTH']
    table_user_name = os.environ['TABLE_USER']

    user_id = event.get('user_id')
    tenant_id = event.get('tenant_id')
    password = event.get('password')
    if not user_id or not tenant_id or not password:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: user_id, tenant_id, or password.'
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
            'body': 'User not found.'
        }

    db_password = response['Item'].get('password')
    if verify_password(db_password, password):
        return {
            'statusCode': 403,
            'body': 'Wrong password.'
        }

    # Create an auth token
    token = bcrypt.gensalt().decode()

    table_auth.put_item(
        Item={
            'token': token,
            'tenant_id': tenant_id,
            'user_id': user_id,
            'expires_at': (datetime.now() + expire_time).isoformat()
        }
    )

    return {
        'statusCode': 200,
        'body': {
            'token': token,
            'expires_at': (datetime.now() + expire_time).isoformat()
        }
    }
