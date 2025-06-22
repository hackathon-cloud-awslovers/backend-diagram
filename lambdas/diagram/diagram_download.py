import boto3
import os
import json
from utils import validate_token

def lambda_handler(event, context):
    """
    Generate pre-signed URL for downloading diagram from S3 (auth required).
    """

    s3_bucket = os.environ['S3_BUCKET_DIAGRAM']

    # Parse query params
    params = event.get('query') or {}
    tenant_id = params.get('tenant_id')
    diagram_id = params.get('diagram_id')

    if not tenant_id or not diagram_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: tenant_id or diagram_id.'}),
            'headers': {
                'Content-Type': 'application/json'
            }
        }

    # Parse token from Authorization header
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

    s3 = boto3.client('s3')

    try:
        presigned_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': s3_bucket, 'Key': file_key},
            ExpiresIn=3600  # 1 hour
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'download_url': presigned_url,
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
