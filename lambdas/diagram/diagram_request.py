import boto3

def lambda_handler(event, context):
    """
    Lambda function to get a diagram.
    """


    diagram_id = event.get('diagram_id')
    tenant_id = event.get('tenant_id')

    if not diagram_id or not tenant_id:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: diagram_id or tenant_id.'
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('diagram_table')

    # Retrieve the diagram from DynamoDB
    response = table.get_item(
        Key={
            'tenant_id': tenant_id,
            'diagram_id': diagram_id
        }
    )

    if 'Item' not in response:
        return {
            'statusCode': 404,
            'body': f'Diagram {diagram_id} not found for tenant {tenant_id}.'
        }

    return {
        'statusCode': 200,
        'body': response['Item']
    }