import json
import boto3
import os
import decimal

dynamodb = boto3.resource('dynamodb')
SURVEY_INSIGHTS_TABLE = os.environ.get('SURVEY_INSIGHTS_TABLE', 'SurveyInsights')

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
def lambda_handler(event, context):
    try:
        # Handle preflight OPTIONS request
        if event.get('httpMethod', '').upper() == 'OPTIONS':
            return {'statusCode': 200, 'headers': cors_headers(event), 'body': ''}

        params = event.get('queryStringParameters') or {}
        user_id = params.get('user_id') if params else None
        table = dynamodb.Table(SURVEY_INSIGHTS_TABLE)
        if user_id:
            # Query all insights for a user
            resp = table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )
            items = resp.get('Items', [])
            return { 'statusCode': 200, 'headers': cors_headers(event), 'body': json.dumps({'insights': convert_decimal(items)}) }
        else:
            # Scan all insights (not recommended for large tables)
            resp = table.scan()
            items = resp.get('Items', [])
            return { 'statusCode': 200, 'headers': cors_headers(event), 'body': json.dumps({'insights': convert_decimal(items)}) }
    except Exception as e:
        return { 'statusCode': 500, 'headers': cors_headers(event), 'body': json.dumps({'error': str(e)}) }