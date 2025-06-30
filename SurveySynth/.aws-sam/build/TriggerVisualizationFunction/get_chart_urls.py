import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
SURVEY_INSIGHTS_TABLE = os.environ.get('SURVEY_INSIGHTS_TABLE', 'SurveyInsights')
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
    user_id = event.get('queryStringParameters', {}).get('user_id')
    upload_id = event.get('queryStringParameters', {}).get('upload_id')
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'GET,OPTIONS'
    }
    if not user_id or not upload_id:
        return {
            'statusCode': 400,
            'headers': cors_headers(event),
            'body': json.dumps({'error': 'user_id and upload_id are required'})
        }
    table = dynamodb.Table(SURVEY_INSIGHTS_TABLE)
    try:
        resp = table.get_item(Key={'user_id': user_id, 'upload_id': upload_id})
        if 'Item' not in resp:
            return {
                'statusCode': 404,
                'headers': cors_headers(event),
                'body': json.dumps({'error': 'Not found'})
            }
        # chart_urls = resp['Item'].get('chart_urls', [])
        chart_urls = resp['Item'].get('chart_urls', [])
        if not isinstance(chart_urls, list):
            chart_urls = [chart_urls] if chart_urls else []
        # return {
        #     'statusCode': 200,
        #     'headers': headers,
        #     'body': json.dumps({'chart_urls': chart_urls})
        # }
        return {
            'statusCode': 200,
            'headers': cors_headers(event),
            'body': json.dumps({'chart_urls': chart_urls})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': cors_headers(event),
            'body': json.dumps({'error': str(e)})
        }