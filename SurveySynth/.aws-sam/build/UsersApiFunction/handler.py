import json
import boto3
import os
import decimal

dynamodb = boto3.resource('dynamodb')
USERS_TABLE = os.environ.get('USERS_TABLE', 'Users')

def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj

def lambda_handler(event, context):
    headers = {
        'Access-Control-Allow-Origin': 'http://localhost:5173',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    try:
        # Handle preflight OPTIONS request
        if event.get('httpMethod', '').upper() == 'OPTIONS':
            return {'statusCode': 200, 'headers': headers, 'body': ''}

        params = event.get('queryStringParameters') or {}
        email = params.get('email') if params else None
        table = dynamodb.Table(USERS_TABLE)
        if email:
            # Get a single user by email
            resp = table.get_item(Key={'email': email})
            item = resp.get('Item')
            if not item:
                return { 'statusCode': 404, 'headers': headers, 'body': json.dumps({'error': 'User not found'}) }
            return { 'statusCode': 200, 'headers': headers, 'body': json.dumps(convert_decimal(item)) }
        else:
            # Scan all users (for user count, etc.)
            resp = table.scan(ProjectionExpression='user_id, email, created_at, upload_count')
            items = resp.get('Items', [])
            return { 'statusCode': 200, 'headers': headers, 'body': json.dumps({'users': convert_decimal(items), 'user_count': len(items)}) }
    except Exception as e:
        return { 'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)}) }
