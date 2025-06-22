import boto3

def lambda_handler(event, context):
    """
    Lambda Function to handle diagram upload.
    """

    diagram_id = event.get('diagram_id')
    tenant_id = event.get('tenant_id')
    file_content = event.get('file_content')

    if not diagram_id or not tenant_id or not file_content:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: diagram_id, tenant_id, or file_content.'
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('diagram_table')

    # Store the diagram in DynamoDB
    response = table.put_item(
        Item={
            'tenant_id': tenant_id,
            'diagram_id': diagram_id,
            'file_content': file_content
        }
    )

    return {
        'statusCode': 200,
        'body': f'Diagram {diagram_id} uploaded successfully.'
    }