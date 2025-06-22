import boto3
import os

def lambda_handler(event, context):
    """
    Lambda function to delete a diagram.
    """
    bucket_name = os.environ['S3_BUCKET_NAME']
    diagram_id = event.get('diagram_id')
    tenant_id = event.get('tenant_id')

    if not diagram_id or not tenant_id:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: diagram_id or tenant_id.'
        }

    dynamodb = boto3.resource('dynamodb')
    s3 = boto3.client('s3')
    table = dynamodb.Table('diagram_table')

    # Delete the diagram
    response = table.delete_item(
        Key={
            'tenant_id': tenant_id,
            'diagram_id': diagram_id
        }
    )
    s3.delete_object(
        Bucket=bucket_name,
        Key=f'{tenant_id}/{diagram_id}'
    )

    return {
        'statusCode': 200,
        'body': f'Diagram {diagram_id} deleted successfully.'
    }