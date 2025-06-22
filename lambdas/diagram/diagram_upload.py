import boto3
import os
import json

ALLOWED_EXTENSIONS = ('.sql', '.json', '.dbml')

def lambda_handler(event, context):
    """
    Generate pre-signed URL for uploading diagram to S3
    """
    body = json.loads(event.get('body', '{}'))

    tenant_id = body.get('tenant_id')
    diagram_id = body.get('diagram_id')

    if not tenant_id or not diagram_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required parameters: tenant_id or diagram_id.'})
        }

    # Validate diagram_id extension
    if not diagram_id.endswith(ALLOWED_EXTENSIONS):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid file extension. Allowed extensions are: {ALLOWED_EXTENSIONS}'})
        }

    s3_bucket = os.environ['S3_BUCKET_DIAGRAM']
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
            'body': json.dumps({'error': str(e)})
        }
