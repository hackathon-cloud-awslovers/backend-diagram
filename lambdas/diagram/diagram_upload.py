import boto3
import os
import json
import io
import cgi
import base64
from utils import validate_token

ALLOWED_EXTENSIONS = ('.sql', '.json', '.dbml')

def lambda_handler(event, context):
    """
    Lambda endpoint to upload file directly to S3 (with auth).
    """
    s3_bucket = os.environ['S3_BUCKET_DIAGRAM']
    s3 = boto3.client('s3')

    # Parse Authorization header
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

    # Decode body (API Gateway delivers body as base64-encoded for binary content)
    content_type = event.get('headers', {}).get('Content-Type') or event.get('headers', {}).get('content-type')
    body_bytes = base64.b64decode(event['body'])
    fp = io.BytesIO(body_bytes)

    # Parse multipart/form-data
    env = {'REQUEST_METHOD': 'POST'}
    headers = {'content-type': content_type}
    form = cgi.FieldStorage(fp=fp, environ=env, headers=headers)

    # Get form fields
    tenant_id = form.getvalue('tenant_id')
    diagram_id = form.getvalue('diagram_id')
    file_item = form['file']

    # Validate fields
    if not tenant_id or not diagram_id or not file_item:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing tenant_id, diagram_id, or file.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    if not diagram_id.endswith(ALLOWED_EXTENSIONS):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid file extension. Allowed extensions: {ALLOWED_EXTENSIONS}'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

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

    # Upload to S3
    file_key = f'{tenant_id}/{diagram_id}'

    try:
        s3.put_object(
            Bucket=s3_bucket,
            Key=file_key,
            Body=file_item.file.read()
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File uploaded successfully.',
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
