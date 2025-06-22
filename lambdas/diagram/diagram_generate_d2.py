import boto3
import os
import json
import base64
import subprocess
import uuid
from utils import validate_token, load_body

def lambda_handler(event, context):
    """
    Lambda function to generate D2 diagram from base64 source (.d2 file), output PNG to S3.
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

    # Parse JSON body
    try:
        body = load_body(event)
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid JSON body.'}),
            'headers': {'Content-Type': 'application/json'}
        }

    # Extract fields
    tenant_id = body.get('tenant_id')
    diagram_id = body.get('diagram_id') or str(uuid.uuid4()) + '.png'
    d2_source_base64 = body.get('d2_source_base64')

    if not tenant_id or not d2_source_base64:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing tenant_id or d2_source_base64.'}),
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

    # Decode D2 source
    try:
        d2_content = base64.b64decode(d2_source_base64)
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Invalid base64 content for D2 source.'}),
            'headers': {'Content-Type': 'application/json'}
        }

    # Write to temp .d2 file
    tmp_d2_file = f"/tmp/{uuid.uuid4()}.d2"
    with open(tmp_d2_file, 'wb') as f:
        f.write(d2_content)

    # Temp output PNG
    tmp_output_file = f"/tmp/{uuid.uuid4()}.png"

    try:
        # Call D2 binary to generate PNG
        result = subprocess.run(
            ["/opt/bin/d2", tmp_d2_file, tmp_output_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
    except subprocess.CalledProcessError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error generating diagram: {e.stderr.decode()}'}),
            'headers': {'Content-Type': 'application/json'}
        }

    # Upload PNG to S3
    file_key = f"{tenant_id}/{diagram_id}"

    try:
        with open(tmp_output_file, 'rb') as f:
            s3.put_object(Bucket=s3_bucket, Key=file_key, Body=f)

        # Presigned URL
        presigned_url = s3.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': s3_bucket, 'Key': file_key},
            ExpiresIn=3600
        )

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'D2 diagram generated successfully.',
                'download_url': presigned_url,
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
