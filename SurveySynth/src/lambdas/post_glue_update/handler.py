import boto3
import json

dynamodb = boto3.resource('dynamodb')
glue = boto3.client('glue')
table = dynamodb.Table('SurveyMeta')

def lambda_handler(event, context):
    print("Glue Event:", json.dumps(event))

    detail = event['detail']
    status = detail['state']
    job_name = detail['jobName']
    job_run_id = detail['jobRunId']
    
    # Get job run details to access arguments
    try:
        job_run_response = glue.get_job_run(JobName=job_name, RunId=job_run_id)
        args = job_run_response['JobRun'].get('Arguments', {})

        # ✅ Add this safe-check block here
        user_id = args.get('--user_id')
        upload_id = args.get('--upload_id')

        if not user_id or not upload_id:
            print("Missing user_id or upload_id in job arguments.")
            return {'statusCode': 400, 'body': 'Missing required arguments'}

    except Exception as e:
        print(f"Failed to get job run details: {str(e)}")
        return {'statusCode': 500, 'body': f'Failed to get job details: {str(e)}'}

    if status != 'SUCCEEDED':
        print("Job did not succeed, skipping.")
        return {'statusCode': 200, 'body': 'Skipped'}

    s3_silver_path = f"silver/{user_id}/{upload_id}.csv"

    table.update_item(
        Key={'user_id': user_id, 'upload_id': upload_id},
        UpdateExpression="SET #s = :s, s3_path_silver = :p",
        ExpressionAttributeNames={'#s': 'status'},
        ExpressionAttributeValues={
            ':s': 'preprocessed',
            ':p': s3_silver_path
        }
    )

    return {'statusCode': 200, 'body': 'Metadata updated'}
