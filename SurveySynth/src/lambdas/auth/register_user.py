import boto3
import json
import time
import hashlib
import uuid

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('Users')

def lambda_handler(event, context):
    # Handle preflight OPTIONS request
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'http://localhost:5173',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': ''
        }

    try:
        body = json.loads(event['body'])
        email = body['email']
        password = hashlib.sha256(body['password'].encode()).hexdigest()

        # Check the path to determine action
        path = event.get('path', '')
        if path.endswith('/register'):
            table.put_item(Item={
                'email': email,
                'password': password,
                'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'user_id': str(uuid.uuid4()),
                'upload_count': 0
            })

            # table.put_item(Item={
            #     'email': email,
            #     'password': password,
            #     'created_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
            # })
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': 'http://localhost:5173',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({'message': 'User registered'})
            }
        elif path.endswith('/login'):
            resp = table.get_item(Key={'email': email})
            user = resp.get('Item')
            if user and user['password'] == password:
                return {
                    'statusCode': 200,
                    'headers': {
                        'Access-Control-Allow-Origin': 'http://localhost:5173',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST'
                    },
                    'body': json.dumps({
                        'message': 'Login successful',
                        'user_id': user.get('user_id')
                    })
                }
        
    

            # if user and user['password'] == password:
            #     return {
            #         'statusCode': 200,
            #         'headers': {
            #             'Access-Control-Allow-Origin': 'http://localhost:5173',
            #             'Access-Control-Allow-Headers': 'Content-Type',
            #             'Access-Control-Allow-Methods': 'OPTIONS,POST'
            #         },
            #         'body': json.dumps({'message': 'Login successful'})
            #     }
            else:
                return {
                    'statusCode': 401,
                    'headers': {
                        'Access-Control-Allow-Origin': 'http://localhost:5173',
                        'Access-Control-Allow-Headers': 'Content-Type',
                        'Access-Control-Allow-Methods': 'OPTIONS,POST'
                    },
                    'body': json.dumps({'message': 'Invalid credentials'})
                }
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': 'http://localhost:5173',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'OPTIONS,POST'
                },
                'body': json.dumps({'message': 'Invalid path'})
            }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': 'http://localhost:5173',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST'
            },
            'body': json.dumps({'error': str(e)})
        }
