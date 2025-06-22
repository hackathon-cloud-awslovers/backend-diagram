import boto3
import os
import json
import io
import cgi
import base64
import subprocess
import uuid
from utils import validate_token

def lambda_handler(event, context):
    """
    Lambda function to generate D2 diagram from uploaded file.
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

    # Decode multipart/form-data
    content_type = event.get('headers', {}).get('Content-Type') or event.get('headers', {}).get('content-type')
    body_bytes = base64.b64decode(event['body'])
    fp = io.BytesIO(body_bytes)

    env = {'REQUEST_METHOD': 'POST'}
    headers = {'content-type': content_type}
    form = cgi.FieldStorage(fp=fp, environ=env, headers=headers)

    # Fields
    tenant_id = form.getvalue('tenant_id')
    diagram_id = form.getvalue('diagram_id') or str(uuid.uuid4()) + '.png'
    file_item = form['file']

    # Validate fields
    if not tenant_id or not file_item:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing tenant_id or file.'}),
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

    # Save .d2 file to /tmp
    tmp_d2_file = f"/tmp/{uuid.uuid4()}.d2"
    with open(tmp_d2_file, 'wb') as f:
        f.write(file_item.file.read())

    # Output file
    tmp_output_file = f"/tmp/{uuid.uuid4()}.png"

    try:
        # Call d2 binary to generate PNG
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

    with open(tmp_output_file, 'rb') as f:
        s3.put_object(Bucket=s3_bucket, Key=file_key, Body=f)

    # Generate pre-signed URL
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
