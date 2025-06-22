import boto3
import os
import json
from utils import validate_token

def lambda_handler(event, context):
    """
    Lambda function to delete a diagram.
    Validates token header using user-validate Lambda.
    """
    bucket_name = os.environ['S3_BUCKET_NAME']
    table_diagram_name = os.environ['TABLE_DIAGRAM']

    # Get Authorization header
    auth_header = event.get('headers', {}).get('Authorization', '')
    token = auth_header.replace('Bearer ', '').strip()

    # Parse body or query params
    if event.get('body'):
        body = json.loads(event['body'])
        diagram_id = body.get('diagram_id')
        tenant_id = body.get('tenant_id')
    else:
        diagram_id = event.get('queryStringParameters', {}).get('diagram_id')
        tenant_id = event.get('queryStringParameters', {}).get('tenant_id')

    if not token or not diagram_id or not tenant_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: token, tenant_id, diagram_id.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    try:
        # Validar token usando Lambda de validar
        validate_token(token, tenant_id)

        # Proceed to delete
        dynamodb = boto3.resource('dynamodb')
        table_diagram = dynamodb.Table(table_diagram_name)
        s3 = boto3.client('s3')

        # Delete from DynamoDB
        table_diagram.delete_item(
            Key={
                'tenant_id': tenant_id,
                'diagram_id': diagram_id
            }
        )

        # Delete from S3
        s3.delete_object(
            Bucket=bucket_name,
            Key=f'{tenant_id}/{diagram_id}'
        )

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'Diagram {diagram_id} deleted successfully.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except Exception as e:
        print('Error:', str(e))
        return {
            'statusCode': 401,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
