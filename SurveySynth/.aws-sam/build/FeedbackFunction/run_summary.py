import boto3
import json

def format_prompt(responses, base_prompt_path="../../prompts/actionable_prompt.txt"):
    with open(base_prompt_path, "r") as f:
        prompt_base = f.read()
    response_lines = [f"{i+1}. \"{line}\"" for i, line in enumerate(responses)]
    return prompt_base + "\n" + "\n".join(response_lines)

def call_bedrock(prompt, model="anthropic.claude-v2"):
    client = boto3.client("bedrock-runtime")  # Ensure boto3 is v1.28+ with Bedrock support

    body = json.dumps({
        "prompt": prompt,
        "max_tokens_to_sample": 1024,
        "temperature": 0.7,
        "stop_sequences": ["\n\n"]
    })

    response = client.invoke_model(
        modelId=model,
        body=body,
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response['body'].read())
    return result.get("completion", "No output")

if __name__ == "__main__":
    from src.lambdas.process_survey.parser import extract_feedback_from_csv
    responses = extract_feedback_from_csv("SurveySynth/src/test-data/sample-survey.csv")
    batch = responses[:10]  # batch size
    prompt = format_prompt(batch)
    print("Sending to Bedrock...\n")
    output = call_bedrock(prompt)
    print(output)
