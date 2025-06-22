import boto3

def lambda_handler(event, context):
    """
    Lambda function to delete a diagram.
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

    # Delete the diagram
    response = table.delete_item(
        Key={
            'tenant_id': tenant_id,
            'diagram_id': diagram_id
        }
    )

    return {
        'statusCode': 200,
        'body': f'Diagram {diagram_id} deleted successfully.'
    }