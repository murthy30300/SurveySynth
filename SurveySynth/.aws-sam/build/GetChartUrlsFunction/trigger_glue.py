import boto3
import json

glue = boto3.client('glue')
ses = boto3.client('ses')  # Add SES client

def send_email(to_address, subject, body):
    response = ses.send_email(
        Source=to_address,  # The sender's email address (must be verified in SES)
        Destination={
            'ToAddresses': [to_address]
        },
        Message={
            'Subject': {'Data': subject},
            'Body': {
                'Html': {'Data': body},
                'Text': {'Data': 'Your visualization job has completed successfully.'}
            }
        }
    )
    print(f"Email sent! Message ID: {response['MessageId']}")

def lambda_handler(event, context):
    print("DynamoDB Stream Event:", json.dumps(event))

    email_sent = False
    for record in event['Records']:
        if record['eventName'] == 'INSERT':
            new_image = record['dynamodb']['NewImage']
            user_id = new_image['user_id']['S']
            upload_id = new_image['upload_id']['S']
            email = new_image.get('email', {}).get('S', 'your-verified-email@example.com')
            # Launch Glue job
            response = glue.start_job_run(
                JobName='Visual_job',
                Arguments={
                    '--user_id': user_id,
                    '--upload_id': upload_id
                }
            )
            print(f"Started Glue job: {response['JobRunId']}")
            # Wait for Glue job to complete (polling)
            job_run_id = response['JobRunId']
            waiter = glue.get_waiter('job_run_succeeded')
            try:
                waiter.wait(
                    JobName='Visual_job',
                    RunId=job_run_id,
                    WaiterConfig={
                        'Delay': 15,
                        'MaxAttempts': 40
                    }
                )
                # Update DynamoDB tables after charts are generated
                dynamodb = boto3.resource('dynamodb')
                # Update SurveyMeta table
                survey_meta_table = dynamodb.Table('SurveyMeta')
                survey_meta_table.update_item(
                    Key={
                        'user_id': user_id,
                        'upload_id': upload_id
                    },
                    UpdateExpression="SET #st = :new_status, analyzed_at = :now, charts_generated_at = :now",
                    ExpressionAttributeNames={
                        '#st': 'status'
                    },
                    ExpressionAttributeValues={
                        ':new_status': 'charts generated',
                        ':now': int(__import__('time').time())
                    }
                )
                # Update SurveyInsights table (add chart_urls, charts_generated_at, status)
                survey_insights_table = dynamodb.Table('SurveyInsights')
                # This is a placeholder for chart URLs, replace with actual URLs if available
                chart_urls = [f'https://s3.amazonaws.com/surveysynth-uploads/{user_id}/{upload_id}/chart1.png']
                survey_insights_table.update_item(
                    Key={
                        'user_id': user_id,
                        'upload_id': upload_id
                    },
                    UpdateExpression="SET chart_urls = :urls, charts_generated_at = :now, #st = :new_status",
                    ExpressionAttributeNames={
                        '#st': 'status'
                    },
                    ExpressionAttributeValues={
                        ':urls': chart_urls,
                        ':now': int(__import__('time').time()),
                        ':new_status': 'charts generated'
                    }
                )
                # Send success email with HTML template
                html_body = f'''
                <html>
                <head>
                  <style>
                    .container {{
                      font-family: Arial, sans-serif;
                      background: #f9f9f9;
                      padding: 30px;
                      border-radius: 10px;
                      box-shadow: 0 2px 8px #e0e0e0;
                      max-width: 600px;
                      margin: auto;
                    }}
                    .success {{
                      color: #2e7d32;
                      font-size: 1.3em;
                      margin-bottom: 20px;
                    }}
                    .details {{
                      background: #fff;
                      padding: 15px;
                      border-radius: 8px;
                      border: 1px solid #e0e0e0;
                      margin-bottom: 20px;
                    }}
                  </style>
                </head>
                <body>
                  <div class="container">
                    <div class="success">✅ Your visualization job has completed successfully!</div>
                    <div class="details">
                      <b>User ID:</b> {user_id}<br>
                      <b>Upload ID:</b> {upload_id}<br>
                      <b>Job Run ID:</b> {job_run_id}
                    </div>
                    <p>You can now view your results in the SurveySynth dashboard.</p>
                    <p style="font-size:0.9em;color:#888;">Thank you for using SurveySynth!</p>
                  </div>
                </body>
                </html>
                '''
                send_email(
                    to_address=email,
                    subject="Visualization Job Completed",
                    body=html_body
                )
                email_sent = True
            except Exception as e:
                print(f"Glue job did not complete successfully: {e}")

    return {"statusCode": 200, "body": "Triggered visualization job and sent email." if email_sent else "Triggered visualization job."}
#2min 20 seconds