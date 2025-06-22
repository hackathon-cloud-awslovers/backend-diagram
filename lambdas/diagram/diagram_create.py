import boto3
import os
import json
from utils import validate_token

def lambda_handler(event, context):
    """
    Lambda function to create a diagram.
    """
    dynamodb = boto3.resource('dynamodb')
    table_diagram_name = os.environ['TABLE_DIAGRAM']
    table_auth_name = os.environ['TABLE_AUTH']  # <- se necesita la tabla auth

    # Parse body
    body = json.loads(event.get('body', '{}'))

    tenant_id = body.get('tenant_id')
    diagram_id = body.get('diagram_id')

    if not tenant_id or not diagram_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: tenant_id, diagram_id.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # Parse token from Authorization header
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {
            'statusCode': 400,
            'body': {'error': 'Missing or invalid Authorization header.'},
            'headers': {
                'Content-Type': 'application/json'
            }
        }
    token = auth_header.split(' ')[1]

    # Validate token (this will raise Exception if invalid)
    try:
        validate_token(token, tenant_id)
    except Exception as e:
        return {
            'statusCode': 403,
            'body': {'error': str(e)},
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # Fetch user_id from TABLE_AUTH (DynamoDB)
    table_auth = dynamodb.Table(table_auth_name)
    response = table_auth.get_item(
        Key={
            'token': token,
            'tenant_id': tenant_id
        }
    )

    if 'Item' not in response:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': 'Token not found.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    user_id = response['Item'].get('user_id')

    # Insert new diagram record
    table_diagram = dynamodb.Table(table_diagram_name)
    table_diagram.put_item(
        Item={
            'tenant_id': tenant_id,
            'diagram_id': diagram_id,
            'user_id': user_id
        }
    )

    return {
        'statusCode': 200,
        'body': {'message': 'Diagram created successfully.', 'user_id': user_id},
        'headers': {
            'Content-Type': 'application/json'
        }
    }
