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
            'body': json.dumps({'error': 'Missing required parameters: token, tenant_id.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
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
        # Token inválido → no devolver Authorization
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Token not found or already logged out.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # Token válido → eliminar
    table_auth.delete_item(
        Key={
            'token': token,
            'tenant_id': tenant_id
        }
    )

    # Token válido → devolver Authorization
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'User logout successfully.'}),
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    }
