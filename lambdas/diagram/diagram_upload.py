import boto3
import os
import json
import base64
from utils import validate_token

ALLOWED_EXTENSIONS = ('.sql', '.json', '.dbml')

def lambda_handler(event, context):
    """
    Lambda endpoint to upload file directly to S3 (with auth) — base64 version.
    """
    s3_bucket = os.environ['S3_BUCKET_DIAGRAM']
    s3 = boto3.client('s3')

    # Authorization header
    auth_header = event.get('headers', {}).get('Authorization', '')
    if not auth_header or not auth_header.startswith('Bearer '):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing or invalid Authorization header.'}),
            'headers': {'Content-Type': 'application/json'}
        }

    token = auth_header.split(' ')[1]

    # Decode body (json)
    try:
        body = json.loads(event['body'])
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON body.'}),
            'headers': {'Content-Type': 'application/json'}
        }

    # Get fields
    tenant_id = body.get('tenant_id')
    diagram_id = body.get('diagram_id')
    file_base64 = body.get('file_base64')

    if not tenant_id or not diagram_id or not file_base64:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing tenant_id, diagram_id, or file_base64.'}),
            'headers': {'Content-Type': 'application/json'}
        }

    if not diagram_id.endswith(ALLOWED_EXTENSIONS):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid file extension. Allowed extensions: {ALLOWED_EXTENSIONS}'}),
            'headers': {'Content-Type': 'application/json'}
        }

    # Validate token
    try:
        validate_token(token, tenant_id)
    except Exception as e:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }

    # Decode file content
    try:
        file_content = base64.b64decode(file_base64)
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid base64 content.'}),
            'headers': {'Content-Type': 'application/json'}
        }

    # Upload to S3
    file_key = f'{tenant_id}/{diagram_id}'

    try:
        s3.put_object(
            Bucket=s3_bucket,
            Key=file_key,
            Body=file_content
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File uploaded successfully.',
                'file_key': file_key
            }),
            'headers': {'Content-Type': 'application/json'}
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)}),
            'headers': {'Content-Type': 'application/json'}
        }
