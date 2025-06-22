import boto3
import json
import os

def validate_token(token, tenant_id):
    if not token or not tenant_id:
        raise Exception('Token inválido o expirado')

    lambda_client = boto3.client('lambda')

    payload = {
        'token': token,
        'tenant_id': tenant_id
    }

    stage = os.environ.get('STAGE', 'dev')
    validate_lambda_name = f'hack-user-service-{stage}-user-validate'

    response = lambda_client.invoke(
        FunctionName=validate_lambda_name,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload).encode('utf-8')
    )

    result_payload = json.loads(response['Payload'].read().decode('utf-8'))
    print('Validate Lambda response:', result_payload)

    if result_payload.get('statusCode') == 403:
        raise Exception('Token inválido o expirado')

    return True