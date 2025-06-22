import boto3
import os
import json
import requests
from utils import validate_token, load_body

ALLOWED_EXTENSIONS = ('.sql', '.json', '.dbml')

def lambda_handler(event, context):
    """
    Lambda function to download a file from external URL and upload to S3, with token auth.
    """

    s3_bucket = os.environ['S3_BUCKET_DIAGRAM']

    # Parse body
    body = load_body(event)

    tenant_id = body.get('tenant_id')
    diagram_id = body.get('diagram_id')
    url = body.get('url')

    if not tenant_id or not diagram_id or not url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: tenant_id, diagram_id, url.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

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

    file_key = f'{tenant_id}/{diagram_id}'

    try:
        # Descargar desde URL externa
        file_response = requests.get(url)
        file_response.raise_for_status()
        file_content = file_response.content

        # Subir a S3
        s3 = boto3.client('s3')
        s3.put_object(Bucket=s3_bucket, Key=file_key, Body=file_content)

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File uploaded successfully from URL.',
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
