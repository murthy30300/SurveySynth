import json
import boto3
import os
import decimal

dynamodb = boto3.resource('dynamodb')
SURVEY_META_TABLE = os.environ.get('SURVEY_META_TABLE', 'SurveyMeta')

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
        user_id = params.get('user_id') if params else None
        table = dynamodb.Table(SURVEY_META_TABLE)
        if user_id:
            # Query all surveys for a user
            resp = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )
            items = resp.get('Items', [])
            return { 'statusCode': 200, 'headers': headers, 'body': json.dumps({'surveys': convert_decimal(items), 'upload_count': len(items)}) }
        else:
            # Scan all surveys (not recommended for large tables)
            resp = table.scan()
            items = resp.get('Items', [])
            return { 'statusCode': 200, 'headers': headers, 'body': json.dumps({'surveys': convert_decimal(items)}) }
    except Exception as e:
        return { 'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)}) }
