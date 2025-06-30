import boto3
import json
import pandas as pd
import io
from datetime import datetime
from decimal import Decimal
import math

# Initialize clients
s3 = boto3.client('s3')
bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
dynamodb = boto3.resource('dynamodb')

# Tables
survey_meta_table = dynamodb.Table('SurveyMeta')
insights_table = dynamodb.Table('SurveyInsights')

def lambda_handler(event, context):
    print("DynamoDB Event:", json.dumps(event))
    
    # Handle DynamoDB Stream event
    for record in event['Records']:
        if record['eventName'] in ['INSERT', 'MODIFY']:
            # Get the new image (updated record)
            new_image = record['dynamodb'].get('NewImage', {})
            
            # Check if status changed to 'preprocessed'
            status = new_image.get('status', {}).get('S', '')
            if status != 'preprocessed':
                continue
                
            user_id = new_image.get('user_id', {}).get('S', '')
            upload_id = new_image.get('upload_id', {}).get('S', '')
            s3_silver_path = new_image.get('s3_path_silver', {}).get('S', '')
            
            if not all([user_id, upload_id, s3_silver_path]):
                print("Missing required fields, skipping record")
                continue
                
            try:
                # Process the feedback
                insights = process_feedback(user_id, upload_id, s3_silver_path)
                
                # Store insights
                store_insights(user_id, upload_id, insights)
                
                # Update survey meta status
                update_survey_status(user_id, upload_id, 'analyzed')
                
                print(f"Successfully analyzed feedback for {user_id}/{upload_id}")
                
            except Exception as e:
                print(f"Error processing feedback for {user_id}/{upload_id}: {str(e)}")
                update_survey_status(user_id, upload_id, 'analysis_failed')
    
    return {'statusCode': 200, 'body': 'Processing completed'}

def process_feedback(user_id, upload_id, s3_silver_path):
    """Process feedback data and generate insights using Bedrock"""
    
    # Parse S3 path
    bucket = 'surveysynth-uploads'  # Use your actual bucket name
    key = s3_silver_path  # The path already contains the correct key
    
    print(f"Attempting to read from bucket: {bucket}, key: {key}")
    
    # Download and read the processed CSV
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(io.BytesIO(response['Body'].read()))
        print(f"Loaded {len(df)} survey responses")
    except Exception as e:
        raise Exception(f"Failed to load CSV from S3: {str(e)}")
    
    # Identify feedback columns
    feedback_columns = [
        'liked_most', 
        'improvement_suggestions', 
        'additional_comments',
        'feedback_text',
        'needs_more_emphasis'
    ]
    
    # Filter existing columns
    available_feedback_cols = [col for col in feedback_columns if col in df.columns]
    print(f"Available feedback columns: {available_feedback_cols}")
    
    if not available_feedback_cols:
        raise Exception("No feedback columns found in the data")
    
    # Extract and clean feedback data
    feedback_data = []
    for _, row in df.iterrows():
        response_feedback = {}
        for col in available_feedback_cols:
            value = str(row[col]).strip() if pd.notna(row[col]) else ""
            if value and value.lower() not in ['nan', 'none', '']:
                response_feedback[col] = value
        
        if response_feedback:  # Only add if there's actual feedback
            feedback_data.append(response_feedback)
    
    print(f"Extracted {len(feedback_data)} responses with feedback")
    
    if not feedback_data:
        return {
            'overall_sentiment': 'Neutral',
            'pain_points': ['No specific feedback provided'],
            'top_insights': ['Limited feedback data available for analysis'],
            'response_count': len(df),
            'feedback_count': 0
        }
    
    # Chunk responses (10-20 per chunk)
    chunk_size = 15
    chunks = [feedback_data[i:i + chunk_size] for i in range(0, len(feedback_data), chunk_size)]
    
    all_insights = []
    
    for i, chunk in enumerate(chunks):
        print(f"Processing chunk {i+1}/{len(chunks)} with {len(chunk)} responses")
        chunk_insights = analyze_chunk_with_bedrock(chunk, i+1, len(chunks))
        all_insights.append(chunk_insights)
    
    # Combine insights from all chunks
    final_insights = combine_insights(all_insights, len(feedback_data), len(df))
    
    return final_insights

def analyze_chunk_with_bedrock(feedback_chunk, chunk_num, total_chunks):
    """Analyze a chunk of feedback using Amazon Bedrock"""
    
    # Prepare the feedback text for analysis
    feedback_text = ""
    for i, response in enumerate(feedback_chunk, 1):
        feedback_text += f"\n--- Response {i} ---\n"
        for column, text in response.items():
            feedback_text += f"{column.replace('_', ' ').title()}: {text}\n"
    
    # Create the prompt
    prompt = f"""
You are an expert at analyzing educational survey feedback. Please analyze the following survey responses from students about a Full Stack Development course.

Survey Responses:
{feedback_text}

Please provide a structured analysis in the following JSON format:
{{
    "sentiment_scores": {{
        "positive": <percentage>,
        "neutral": <percentage>, 
        "negative": <percentage>
    }},
    "pain_points": [
        "pain point 1",
        "pain point 2",
        "pain point 3"
    ],
    "positive_aspects": [
        "positive aspect 1",
        "positive aspect 2", 
        "positive aspect 3"
    ],
    "actionable_insights": [
        "specific actionable insight 1",
        "specific actionable insight 2",
        "specific actionable insight 3"
    ],
    "topics_mentioned": [
        "topic 1",
        "topic 2"
    ]
}}

Focus on:
1. Overall sentiment distribution
2. Common pain points and complaints
3. What students liked most
4. Specific, actionable recommendations for course improvement
5. Technical topics that need more/less emphasis

Respond with valid JSON only.
"""

    try:
        # Call Bedrock Claude
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-haiku-20240307-v1:0',
            contentType='application/json',
            accept='application/json',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 2000,
                'messages': [
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.3
            })
        )
        
        # Parse response
        response_body = json.loads(response['body'].read())
        analysis_text = response_body['content'][0]['text']
        
        # Extract JSON from response
        try:
            # Find JSON in the response
            start_idx = analysis_text.find('{')
            end_idx = analysis_text.rfind('}') + 1
            json_str = analysis_text[start_idx:end_idx]
            analysis_result = json.loads(json_str)
            
            print(f"Chunk {chunk_num} analysis completed successfully")
            return analysis_result
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON from Bedrock response: {str(e)}")
            print(f"Raw response: {analysis_text}")
            
            # Fallback analysis
            return {
                "sentiment_scores": {"positive": 50, "neutral": 30, "negative": 20},
                "pain_points": ["Unable to parse detailed analysis"],
                "positive_aspects": ["Analysis completed"],
                "actionable_insights": ["Review feedback analysis system"],
                "topics_mentioned": ["General feedback"]
            }
            
    except Exception as e:
        print(f"Bedrock analysis failed for chunk {chunk_num}: {str(e)}")
        
        # Fallback analysis
        return {
            "sentiment_scores": {"positive": 50, "neutral": 30, "negative": 20},
            "pain_points": ["Analysis service unavailable"],
            "positive_aspects": ["Feedback collected successfully"],
            "actionable_insights": ["Retry analysis when service is available"],
            "topics_mentioned": ["System feedback"]
        }

def combine_insights(chunk_insights, feedback_count, total_responses):
    """Combine insights from multiple chunks into final analysis"""
    
    if not chunk_insights:
        return {
            'overall_sentiment': 'Neutral',
            'pain_points': ['No insights generated'],
            'top_insights': ['Analysis could not be completed'],
            'response_count': total_responses,
            'feedback_count': feedback_count
        }
    
    # Aggregate sentiment scores
    total_positive = sum(chunk.get('sentiment_scores', {}).get('positive', 0) for chunk in chunk_insights)
    total_neutral = sum(chunk.get('sentiment_scores', {}).get('neutral', 0) for chunk in chunk_insights)
    total_negative = sum(chunk.get('sentiment_scores', {}).get('negative', 0) for chunk in chunk_insights)
    
    num_chunks = len(chunk_insights)
    avg_positive = total_positive / num_chunks if num_chunks > 0 else 0
    avg_neutral = total_neutral / num_chunks if num_chunks > 0 else 0
    avg_negative = total_negative / num_chunks if num_chunks > 0 else 0
    
    # Determine overall sentiment
    if avg_positive > avg_negative and avg_positive > 40:
        overall_sentiment = 'Positive'
    elif avg_negative > avg_positive and avg_negative > 40:
        overall_sentiment = 'Negative'
    else:
        overall_sentiment = 'Mixed'
    
    # Aggregate pain points and insights
    all_pain_points = []
    all_insights = []
    all_positive_aspects = []
    
    for chunk in chunk_insights:
        all_pain_points.extend(chunk.get('pain_points', []))
        all_insights.extend(chunk.get('actionable_insights', []))
        all_positive_aspects.extend(chunk.get('positive_aspects', []))
    
    # Remove duplicates and get top items
    unique_pain_points = list(dict.fromkeys(all_pain_points))[:5]
    unique_insights = list(dict.fromkeys(all_insights))[:3]
    unique_positive = list(dict.fromkeys(all_positive_aspects))[:3]
    print(f"Aggregated unique positive_aspects: {unique_positive}")

    # If no positive aspects found, add a default message
    if not unique_positive:
        unique_positive = ["No specific positive aspects identified"]

    # --- Begin logic for avg_satisfaction and topic_sentiment_map ---
    # We'll try to extract topic ratings from chunk_insights if present
    # and also compute avg_satisfaction if a 'satisfaction' or similar field is present.
    # This is a best-effort approach based on the structure of chunk_insights.

    topic_sentiment_map = {}
    satisfaction_scores = []
    topic_counts = {}

    for chunk in chunk_insights:
        # If chunk has topics_mentioned and sentiment_scores, try to aggregate
        topics = chunk.get('topics_mentioned', [])
        sentiment = chunk.get('sentiment_scores', {})
        # If chunk has topic_ratings, use them (custom extension, not in prompt)
        topic_ratings = chunk.get('topic_ratings', {})
        # If chunk has avg_satisfaction, use it (custom extension, not in prompt)
        if 'avg_satisfaction' in chunk:
            satisfaction_scores.append(chunk['avg_satisfaction'])
        # If chunk has satisfaction_score, use it (custom extension, not in prompt)
        if 'satisfaction_score' in chunk:
            satisfaction_scores.append(chunk['satisfaction_score'])

        # Try to build topic_sentiment_map from topic_ratings if present
        if topic_ratings:
            for topic, rating_info in topic_ratings.items():
                if topic not in topic_sentiment_map:
                    topic_sentiment_map[topic] = {
                        'avg_rating': 0.0,
                        'positive_count': 0,
                        'negative_count': 0,
                        'total_rating': 0.0,
                        'count': 0
                    }
                topic_sentiment_map[topic]['total_rating'] += rating_info.get('avg_rating', 0.0)
                topic_sentiment_map[topic]['count'] += 1
                topic_sentiment_map[topic]['positive_count'] += rating_info.get('positive_count', 0)
                topic_sentiment_map[topic]['negative_count'] += rating_info.get('negative_count', 0)
        # If not, try to count topics for positive/negative from sentiment
        elif topics and sentiment:
            for topic in topics:
                if topic not in topic_sentiment_map:
                    topic_sentiment_map[topic] = {
                        'avg_rating': 0.0,
                        'positive_count': 0,
                        'negative_count': 0,
                        'total_rating': 0.0,
                        'count': 0
                    }
                # Heuristic: if positive > negative, count as positive, else negative
                if sentiment.get('positive', 0) > sentiment.get('negative', 0):
                    topic_sentiment_map[topic]['positive_count'] += 1
                else:
                    topic_sentiment_map[topic]['negative_count'] += 1
                topic_sentiment_map[topic]['count'] += 1

    # Finalize avg_rating for each topic
    for topic, info in topic_sentiment_map.items():
        if info['count'] > 0:
            info['avg_rating'] = round(info['total_rating'] / info['count'], 2) if info['total_rating'] > 0 else 0.0
        # Remove helper fields
        del info['total_rating']
        del info['count']

    # Compute avg_satisfaction
    if satisfaction_scores:
        avg_satisfaction = round(sum(satisfaction_scores) / len(satisfaction_scores), 2)
    else:
        # If not available, try to estimate from sentiment (e.g., map positive/neutral/negative to 5/3/1)
        total_score = 0
        total_count = 0
        for chunk in chunk_insights:
            sentiment = chunk.get('sentiment_scores', {})
            if sentiment:
                total = sum(sentiment.values())
                if total > 0:
                    score = (
                        sentiment.get('positive', 0) * 5 +
                        sentiment.get('neutral', 0) * 3 +
                        sentiment.get('negative', 0) * 1
                    ) / total
                    total_score += score
                    total_count += 1
        avg_satisfaction = round(total_score / total_count, 2) if total_count > 0 else 0.0

    return {
        'overall_sentiment': overall_sentiment,
        'sentiment_breakdown': {
            'positive': round(avg_positive, 1),
            'neutral': round(avg_neutral, 1),
            'negative': round(avg_negative, 1)
        },
        'pain_points': unique_pain_points,
        'positive_aspects': unique_positive,
        'top_insights': unique_insights,
        'response_count': total_responses,
        'feedback_count': feedback_count,
        'analysis_chunks': num_chunks,
        'avg_satisfaction': avg_satisfaction,
        'topic_sentiment_map': topic_sentiment_map
    }

def store_insights(user_id, upload_id, insights_data):
    """Store insights in DynamoDB matching the SurveyInsights table structure"""
    try:
        # Convert any float values to Decimal for DynamoDB compatibility
        def convert_floats_to_decimal(obj):
            if isinstance(obj, float):
                return Decimal(str(obj))
            elif isinstance(obj, dict):
                return {key: convert_floats_to_decimal(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_floats_to_decimal(item) for item in obj]
            else:
                return obj
        
        # Example: fetch total_survey_count and completed_analyses for the user
        # You should implement actual logic to fetch these from your DB as needed
        total_survey_count = 0
        completed_analyses = 0
        try:
            # Count all surveys for this user
            response = survey_meta_table.query(
                KeyConditionExpression=boto3.dynamodb.conditions.Key('user_id').eq(user_id)
            )
            total_survey_count = len(response.get('Items', []))
            completed_analyses = sum(1 for item in response.get('Items', []) if item.get('status') == 'analyzed')
        except Exception as e:
            print(f"Failed to fetch survey counts: {str(e)}")

        item = {
            'user_id': user_id,
            'upload_id': upload_id,
            'analyzed_at': datetime.now().isoformat(),
            'status': 'completed',
            'analysis_chunks': convert_floats_to_decimal(insights_data.get('analysis_chunks', 0)),
            'feedback_count': convert_floats_to_decimal(insights_data.get('feedback_count', 0)),
            'response_count': convert_floats_to_decimal(insights_data.get('response_count', 0)),
            'overall_sentiment': insights_data.get('overall_sentiment', 'neutral'),
            'sentiment_breakdown': convert_floats_to_decimal(insights_data.get('sentiment_breakdown', {})),
            'top_insights': convert_floats_to_decimal(insights_data.get('top_insights', [])),
            'positive_aspects': convert_floats_to_decimal(insights_data.get('positive_aspects', [])),  # <-- Ensure always present
            'pain_points': convert_floats_to_decimal(insights_data.get('pain_points', [])),
            'total_survey_count': convert_floats_to_decimal(total_survey_count),
            'completed_analyses': convert_floats_to_decimal(completed_analyses),
            'avg_satisfaction': convert_floats_to_decimal(insights_data.get('avg_satisfaction', 0.0)),
            'topic_sentiment_map': convert_floats_to_decimal(insights_data.get('topic_sentiment_map', {}))
        }
        # Store in DynamoDB
        insights_table.put_item(Item=item)
        print(f"Insights stored successfully for {user_id}/{upload_id}")
        
    except Exception as e:
        raise Exception(f"Failed to store insights: {str(e)}")

def update_survey_status(user_id, upload_id, status):
    """Update the survey metadata status"""
    
    try:
        survey_meta_table.update_item(
            Key={'user_id': user_id, 'upload_id': upload_id},
            UpdateExpression="SET #s = :s, analyzed_at = :t",
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':s': status,
                ':t': datetime.now().isoformat()
            }
        )
        print(f"Survey status updated to {status} for {user_id}/{upload_id}")
        
    except Exception as e:
        print(f"Failed to update survey status: {str(e)}")
        raise