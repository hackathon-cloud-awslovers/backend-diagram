import boto3
import os
import json
from utils import validate_token, load_body

ALLOWED_EXTENSIONS = ('.sql', '.json', '.dbml')

def lambda_handler(event, context):
    """
    Generate pre-signed URL for uploading diagram to S3 (auth required).
    Must verify that diagram_id exists in diagram table.
    """

    dynamodb = boto3.resource('dynamodb')
    s3_bucket = os.environ['S3_BUCKET_DIAGRAM']
    table_diagram_name = os.environ['TABLE_DIAGRAM']

    # Parse body
    body = load_body(event)

    tenant_id = body.get('tenant_id')
    diagram_id = body.get('diagram_id')

    if not tenant_id or not diagram_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: tenant_id or diagram_id.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # Validate diagram_id extension
    if not diagram_id.endswith(ALLOWED_EXTENSIONS):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid file extension. Allowed extensions are: {ALLOWED_EXTENSIONS}'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # Read Authorization header
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing or invalid Authorization header.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    token = auth_header.split(' ')[1]

    # Validate token
    try:
        validate_token(token, tenant_id)
    except Exception as e:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # Verify if diagram_id exists in table
    table_diagram = dynamodb.Table(table_diagram_name)
    response = table_diagram.get_item(
        Key={
            'tenant_id': tenant_id,
            'diagram_id': diagram_id
        }
    )

    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Diagram {diagram_id} not found for tenant {tenant_id}. Please create it first.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # Generate pre-signed URL
    file_key = f'{tenant_id}/{diagram_id}'
    s3 = boto3.client('s3')

    try:
        presigned_url = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={'Bucket': s3_bucket, 'Key': file_key},
            ExpiresIn=3600  # 1 hour
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'upload_url': presigned_url,
                'file_key': file_key
            }),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }
