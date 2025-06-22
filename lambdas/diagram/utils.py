import boto3
import json
import os

def payload_token(token, tenant_id):
    if not token or not tenant_id:
        raise Exception('Token inválido o expirado')

    lambda_client = boto3.client('lambda')

    payload = {
        'tenant_id': tenant_id
    }

    validate_lambda_name = os.environ.get("auth_lambda")

    response = lambda_client.invoke(
        FunctionName=validate_lambda_name,
        InvocationType='RequestResponse',
        Payload=json.dumps({
            'headers': {
                'Authorization': f'Bearer {token}'
            },
            'body': json.dumps(payload)
        }).encode('utf-8')
    )

    result_payload = json.loads(response['Payload'].read().decode('utf-8'))
    print('Validate Lambda response:', result_payload)
    return result_payload

def validate_token(token, tenant_id):
    result_payload = payload_token(token, tenant_id)
    if result_payload.get('statusCode') == 403:
        raise Exception('Token inválido o expirado')

    return True
