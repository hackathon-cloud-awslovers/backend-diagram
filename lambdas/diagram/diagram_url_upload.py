import boto3

def lambda_handler(event, context):
    """
    Lambda function to upload a diagram with URL file.
    """

    diagram_id = event.get('diagram_id')
    tenant_id = event.get('tenant_id')
    file_url = event.get('file_url')

    if not diagram_id or not tenant_id or not file_url:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: diagram_id, tenant_id, or file_url.'
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('diagram_table')

    # Store the diagram URL in DynamoDB
    response = table.put_item(
        Item={
            'tenant_id': tenant_id,
            'diagram_id': diagram_id,
            'file_url': file_url
        }
    )

    return {
        'statusCode': 200,
        'body': f'Diagram {diagram_id} uploaded successfully with URL.'
    }