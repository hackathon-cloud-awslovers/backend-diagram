import json
import boto3
import os

def lambda_handler(event, context):
    table_auth_name = os.environ['TABLE_AUTH']

    # Parse POST body
    body = json.loads(event.get('body', '{}'))

    token = body.get('token')
    tenant_id = body.get('tenant_id')

    if not token or not tenant_id:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: token, tenant_id.'
        }

    dynamodb = boto3.resource('dynamodb')
    table_auth = dynamodb.Table(table_auth_name)

    # Buscar si el token existe
    response = table_auth.get_item(
        Key={
            'token': token,
            'tenant_id': tenant_id
        }
    )

    if 'Item' not in response:
        return {
            'statusCode': 400,
            'body': 'Token not found or already logged out.'
        }

    # Eliminar el token
    table_auth.delete_item(
        Key={
            'token': token,
            'tenant_id': tenant_id
        }
    )

    return {
        'statusCode': 200,
        'body': 'User logout successfully.'
    }
