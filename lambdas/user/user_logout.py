import json
import boto3
import os

def load_body(event):
    if 'body' not in event:
        return event

    if isinstance(event["body"], dict):
        return event['body']
    else:
        return json.loads(event['body'])

def lambda_handler(event, context):
    table_auth_name = os.environ['TABLE_AUTH']

    # Leer token del header
    auth_header = event['headers'].get('Authorization') or event['headers'].get('authorization')

    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
    else:
        token = None

    # Leer tenant_id del body
    body = load_body(event)
    tenant_id = body.get('tenant_id')

    if not token or not tenant_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: token (Authorization header), tenant_id.'}),
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
            'body': {'error': 'Token not found or already logged out.'},
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
        'body': {'message': 'User logout successfully.'},
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {token}'
        }
    }
