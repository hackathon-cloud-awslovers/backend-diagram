import boto3
import os
import json
import uuid
import subprocess
from utils import validate_token

s3_bucket = os.environ['S3_BUCKET_DIAGRAM']
s3 = boto3.client('s3')

def generate_aws(diagram_id, fileitem, tenant_id):
    py_file = f"/tmp/{diagram_id}.py"
    with open(py_file, 'wb') as f:
        f.write(fileitem.file.read())

    try:
        subprocess.run(['python3', py_file], check=True)
    except subprocess.CalledProcessError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error running diagram code: {str(e)}'})
        }

    output_file = f"/tmp/{diagram_id}.png"
    if not os.path.exists(output_file):
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Diagram image not generated'})
        }

    file_key = f'{tenant_id}/{diagram_id}.png'
    s3.upload_file(output_file, s3_bucket, file_key)

    presigned_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': s3_bucket, 'Key': file_key},
        ExpiresIn=3600
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'download_url': presigned_url}),
        'headers': {'Content-Type': 'application/json'}
    }

def generate_sql(diagram_id, fileitem, tenant_id):
    sql_file = f"/tmp/{diagram_id}.sql"
    with open(sql_file, 'wb') as f:
        f.write(fileitem.file.read())

    file_key = f'{tenant_id}/{diagram_id}.sql'
    s3.upload_file(sql_file, s3_bucket, file_key)

    presigned_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': s3_bucket, 'Key': file_key},
        ExpiresIn=3600
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'download_url': presigned_url}),
        'headers': {'Content-Type': 'application/json'}
    }

def generate_json(diagram_id, fileitem, tenant_id):
    json_file = f"/tmp/{diagram_id}.json"
    with open(json_file, 'wb') as f:
        f.write(fileitem.file.read())

    file_key = f'{tenant_id}/{diagram_id}.json'
    s3.upload_file(json_file, s3_bucket, file_key)

    presigned_url = s3.generate_presigned_url(
        ClientMethod='get_object',
        Params={'Bucket': s3_bucket, 'Key': file_key},
        ExpiresIn=3600
    )

    return {
        'statusCode': 200,
        'body': json.dumps({'download_url': presigned_url}),
        'headers': {'Content-Type': 'application/json'}
    }

def lambda_handler(event, context):
    import base64
    import cgi
    import io

    token = event['headers'].get('Authorization') or event['headers'].get('authorization')

    content_type = event['headers'].get('Content-Type') or event['headers'].get('content-type')
    body = base64.b64decode(event['body'])
    fp = io.BytesIO(body)
    env = {'REQUEST_METHOD': 'POST'}
    headers = {'content-type': content_type}

    form = cgi.FieldStorage(fp=fp, environ=env, headers=headers)
    fileitem = form['file']
    tenant_id = form.getvalue('tenant_id')
    diagram_id = form.getvalue('diagram_id') or str(uuid.uuid4())

    if not tenant_id or not fileitem:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing tenant_id or file'})
        }

    try:
        validate_token(token, tenant_id)
    except Exception as e:
        return {
            'statusCode': 403,
            'body': json.dumps({'error': str(e)})
        }

    if diagram_id.endswith('.py'):
        return generate_aws(diagram_id, fileitem, tenant_id)
    elif diagram_id.endswith('.sql'):
        return generate_sql(diagram_id, fileitem, tenant_id)
    elif diagram_id.endswith('.json'):
        return generate_json(diagram_id, fileitem, tenant_id)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Unsupported file type. Only .py, .sql, and .json are allowed.'})
        }

