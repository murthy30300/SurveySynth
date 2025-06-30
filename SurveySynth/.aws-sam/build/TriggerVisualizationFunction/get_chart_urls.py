import boto3
import os
import json

dynamodb = boto3.resource('dynamodb')
SURVEY_INSIGHTS_TABLE = os.environ.get('SURVEY_INSIGHTS_TABLE', 'SurveyInsights')

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
            'headers': headers,
            'body': json.dumps({'error': 'user_id and upload_id are required'})
        }
    table = dynamodb.Table(SURVEY_INSIGHTS_TABLE)
    try:
        resp = table.get_item(Key={'user_id': user_id, 'upload_id': upload_id})
        if 'Item' not in resp:
            return {
                'statusCode': 404,
                'headers': headers,
                'body': json.dumps({'error': 'Not found'})
            }
        chart_urls = resp['Item'].get('chart_urls', [])
        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'chart_urls': chart_urls})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': headers,
            'body': json.dumps({'error': str(e)})
        }