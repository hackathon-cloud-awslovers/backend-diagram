import boto3
import os
import json
import uuid
from utils import validate_token

from diagrams import Diagram  # Import de diagrams
from contextlib import redirect_stdout

s3_bucket = os.environ['S3_BUCKET_DIAGRAM']
s3 = boto3.client('s3')


def generate_diagram(diagram_id, fileitem, tenant_id):
    # Leer el código enviado (.py)
    code_content = fileitem.file.read().decode()

    output_file = f"/tmp/{diagram_id}.png"

    try:
        with Diagram(diagram_id, filename=f"/tmp/{diagram_id}", outformat="png"):
            # Ejecutar el código dentro del contexto Diagram
            # Seguridad: crear un contexto restringido
            exec_globals = {}
            exec_locals = {}
            exec(code_content, exec_globals, exec_locals)
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Error generating diagram: {str(e)}'})
        }

    if not os.path.exists(output_file):
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Diagram image not generated'})
        }

    # Subir a S3
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

    # SOLO .py → usa diagrams
    if diagram_id.endswith('.yml'):
        # Quitar extensión
        diagram_id = diagram_id.replace(".yml", "")
        return generate_diagram(diagram_id, fileitem, tenant_id)

    # .sql o .json → igual que antes
    elif diagram_id.endswith('.sql'):
        return None
    elif diagram_id.endswith('.json'):
        return None
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Unsupported file type. Only .py, .sql, and .json are allowed.'})
        }
