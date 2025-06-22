import boto3
import os
import json
import requests

ALLOWED_EXTENSIONS = ('.sql', '.json', '.dbml')

def lambda_handler(event, context):
    """
    Lambda function to download a file from external URL and upload to S3
    """
    body = json.loads(event.get('body', '{}'))

    tenant_id = body.get('tenant_id')
    diagram_id = body.get('diagram_id')
    url = body.get('url')

    if not tenant_id or not diagram_id or not url:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: tenant_id, diagram_id, url.'})
        }

    if not diagram_id.endswith(ALLOWED_EXTENSIONS):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid file extension. Allowed extensions are: {ALLOWED_EXTENSIONS}'})
        }

    s3_bucket = os.environ['S3_BUCKET_DIAGRAM']
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
            'body': json.dumps({'error': str(e)})
        }
