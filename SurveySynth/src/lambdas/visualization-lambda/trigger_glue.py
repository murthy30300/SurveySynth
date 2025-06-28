import boto3
import json

glue = boto3.client('glue')

def lambda_handler(event, context):
    print("DynamoDB Stream Event:", json.dumps(event))

    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            user_id = new_image['user_id']['S']
            upload_id = new_image['upload_id']['S']
            
            # Launch Glue job
            response = glue.start_job_run(
                JobName='Visual_job',
                Arguments={
                    '--user_id': user_id,
                    '--upload_id': upload_id
                }
            )
            print(f"Started Glue job: {response['JobRunId']}")

    return {"statusCode": 200, "body": "Triggered visualization job."}
