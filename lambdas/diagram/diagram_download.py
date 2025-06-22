import boto3
import os
import json

def lambda_handler(event, context):
    """
    Generate pre-signed URL for downloading diagram from S3
    """
    params = event.get('queryStringParameters') or {}
    tenant_id = params.get('tenant_id')
    diagram_id = params.get('diagram_id')

    if not tenant_id or not diagram_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: tenant_id or diagram_id.'})
        }

    s3_bucket = os.environ['S3_BUCKET_DIAGRAM']
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
            'body': json.dumps({'error': str(e)})
        }
