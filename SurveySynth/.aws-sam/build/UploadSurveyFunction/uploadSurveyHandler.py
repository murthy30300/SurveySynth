import boto3
import json
import uuid
import time
import base64
glue = boto3.client('glue')

dynamodb = boto3.resource('dynamodb')
s3 = boto3.client('s3')

USERS_TABLE = 'Users'
METADATA_TABLE = 'SurveyMeta'
BUCKET_NAME = 'surveysynth-uploads'

def lambda_handler(event, context):
    print('Event received:', json.dumps(event))
    # Handle preflight CORS request
    if event.get('httpMethod') == 'OPTIONS':
        print('OPTIONS preflight request')
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': ''
        }

    try:
        print('Parsing body...')
        body = json.loads(event['body'])
        print('Body:', body)
        email = body['email']  # Using email as lookup key
        file_content = base64.b64decode(body['file'])
        filename = body.get('filename', 'upload.csv')
        print(f'Email: {email}, Filename: {filename}')

        users_table = dynamodb.Table(USERS_TABLE)
        meta_table = dynamodb.Table(METADATA_TABLE)

        # Lookup user by email
        print('Looking up user in DynamoDB...')
        user = users_table.get_item(Key={'email': email}).get('Item')
        print('User found:', user)
        if not user:
            print('User not found!')
            return {
                'statusCode': 404,
                'headers': cors_headers(),
                'body': json.dumps({'error': 'User not found'})
            }

        upload_count = user.get('upload_count', 0)
        new_count = upload_count + 1
        user_id = user['user_id']
        print(f'Upload count: {upload_count}, New count: {new_count}, User ID: {user_id}')

        # Construct S3 key
        object_key = f'raw_data_csv/{user_id}_c{new_count}.csv'
        print(f'Uploading to S3: {object_key}')
        s3.put_object(Bucket=BUCKET_NAME, Key=object_key, Body=file_content)

        # Update upload count in Users
        print('Updating upload count in DynamoDB...')
        users_table.update_item(
            Key={'email': email},
            UpdateExpression='SET upload_count = :val',
            ExpressionAttributeValues={':val': new_count}
        )

        # Write to SurveyMeta table
        upload_id = str(uuid.uuid4())
        print('Writing metadata to SurveyMeta table...')
        meta_table.put_item(Item={
            'user_id': user_id,
            'upload_id': upload_id,
            's3_path_raw': object_key,
            'status': 'raw',
            'timestamp': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        })

        print('Upload successful!')
        response = glue.start_job_run(
        JobName='SurveyPreprocessJob',  # your actual job name
        Arguments={
            '--user_id': user_id,
            '--upload_id': upload_id,
            '--s3_input_path': f's3://{BUCKET_NAME}/{object_key}',
            '--s3_output_path': f's3://{BUCKET_NAME}/silver/{user_id}/{upload_id}.csv'
        })

        print("Glue job started:", response.get("JobRunId"))
        return {
            'statusCode': 200,
            'headers': cors_headers(),
            'body': json.dumps({'message': 'File uploaded', 'upload_id': upload_id})
        }

    except Exception as e:
        print('Exception occurred:', str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers(),
            'body': json.dumps({'error': str(e)})
        }

def cors_headers(event=None):
    allowed_origins = [
        'http://localhost:5173',
        'http://buck30300.s3-website-us-east-1.amazonaws.com'
    ]
    origin = ''
    if event and 'headers' in event and 'origin' in event['headers']:
        origin = event['headers']['origin']
    allow_origin = origin if origin in allowed_origins else allowed_origins[1]
    return {
        'Access-Control-Allow-Origin': allow_origin,
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }