import boto3


def lambda_handler(event, context):
    """
    Lambda function to download a diagram file from S3.
    :param event:
    :param context:
    :return:
    """

    diagram_id = event.get('diagram_id')
    tenant_id = event.get('tenant_id')

    if not diagram_id or not tenant_id:
        return {
            'statusCode': 400,
            'body': 'Missing required parameters: diagram_id or tenant_id.'
        }

    s3 = boto3.client('s3')
    bucket_name = 'your-bucket-name'  # Replace with your S3 bucket name
    file_key = f'{tenant_id}/{diagram_id}.sql'  # Assuming the file is stored as SQL

    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        file_content = response['Body'].read()

        return {
            'statusCode': 200,
            'body': file_content,
            'headers': {
                'Content-Type': 'application/sql'
            }
        }
    except s3.exceptions.NoSuchKey:
        return {
            'statusCode': 404,
            'body': f'Diagram {diagram_id} not found for tenant {tenant_id}.'
        }