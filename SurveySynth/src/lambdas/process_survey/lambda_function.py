import boto3
import json
import csv

s3_client = boto3.client("s3")
bedrock_client = boto3.client("bedrock-runtime")

def extract_feedback_from_s3(bucket, key):
    obj = s3_client.get_object(Bucket=bucket, Key=key)
    lines = obj['Body'].read().decode("utf-8").splitlines()
    reader = csv.DictReader(lines)
    return [row["feedback"] for row in reader if "feedback" in row]

def build_prompt(responses):
    prompt_template = """
Human: You are an expert summarizer helping product teams improve their services.

Below are user responses from a survey. Please do the following:
1. Summarize the overall sentiment of the responses.
2. List the top pain points mentioned.
3. List any positive feedback.
4. Provide the Top 3 actionable suggestions the team should implement.

Respond in this format:
- Summary:
- Pain Points:
- Positive Feedback:
- Top 3 Actionable Suggestions:

Responses:
[FEEDBACK]

Assistant:
""".strip()

    formatted = "\n".join([f'{i+1}. "{resp}"' for i, resp in enumerate(responses)])
    return prompt_template.replace("[FEEDBACK]", formatted)

def lambda_handler(event, context):
    print("Received S3 event:")
    print(json.dumps(event))
    
    # Parse event for bucket and object key
    bucket = event['Records'][0]['s3']['bucket']['name']
    key    = event['Records'][0]['s3']['object']['key']

    # Extract feedback from uploaded CSV
    responses = extract_feedback_from_s3(bucket, key)
    prompt = build_prompt(responses[:10])  # Limit to 10 responses

    print("Prompt sent to Claude:\n", prompt)

    # Prepare Bedrock API payload
    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 1500,
        "temperature": 0.7,
        # "stop_sequences": ["\n\n"]
    })

    # Invoke Claude (Bedrock)
    response = bedrock_client.invoke_model(
        modelId="anthropic.claude-v2",
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    # Read response once and log
    response_body = response['body'].read().decode('utf-8')
    print("Raw Bedrock result:\n", response_body)

    try:
        result_json = json.loads(response_body)
        summary = result_json.get("completion", "No 'completion' field")
        print("Final output:\n", summary)
    except Exception as e:
        print("Could not decode result as JSON:", str(e))

    return {
        'statusCode': 200,
        'body': json.dumps("Bedrock summary generated successfully!")
    }
