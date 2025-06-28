import sys

# args = sys.argv
# user_id = args[args.index('--user_id') + 1] if '--user_id' in args else 'all'
# upload_id = args[args.index('--upload_id') + 1] if '--upload_id' in args else None

# event = {
#     'user_id': user_id,
#     'upload_id': upload_id
# }
# lambda_handler(event, None)

import boto3
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
from datetime import datetime
import numpy as np
from collections import Counter
from wordcloud import WordCloud
import matplotlib.patches as mpatches

# Initialize clients
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Configuration
BUCKET_NAME = 'surveysynth-uploads'
VISUALS_PREFIX = 'visuals/'
insights_table = dynamodb.Table('SurveyInsights')

# Set style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

def lambda_handler(event, context):
    """
    Main handler - can be triggered manually or by API Gateway
    Generates all visualizations for a specific user or all users
    """
    
    # Extract parameters
    user_id = event.get('user_id', 'all')  # 'all' for system-wide analytics
    upload_id = event.get('upload_id', None)  # Specific survey or None for all
    
    try:
        # Fetch data from DynamoDB
        survey_data = fetch_survey_insights(user_id, upload_id)
        
        if not survey_data:
            return {
                'statusCode': 404,
                'body': json.dumps({'message': 'No survey data found'})
            }
        
        # Generate all visualizations
        chart_urls = generate_all_visualizations(survey_data, user_id, upload_id)
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Visualizations generated successfully',
                'charts': chart_urls,
                'total_surveys': len(survey_data)
            })
        }
        
    except Exception as e:
        print(f"Error generating visualizations: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def fetch_survey_insights(user_id, upload_id):
    """Fetch survey insights from DynamoDB"""
    
    try:
        if user_id == 'all':
            # Scan entire table for system-wide analytics
            response = insights_table.scan()
        elif upload_id:
            # Get specific survey
            response = insights_table.get_item(
                Key={'user_id': user_id, 'upload_id': upload_id}
            )
            return [response['Item']] if 'Item' in response else []
        else:
            # Get all surveys for a specific user
            response = insights_table.query(
                KeyConditionExpression='user_id = :uid',
                ExpressionAttributeValues={':uid': user_id}
            )
        
        return response.get('Items', [])
        
    except Exception as e:
        print(f"Error fetching data: {str(e)}")
        return []

def generate_all_visualizations(data, user_id, upload_id):
    """Generate all visualization charts"""
    
    chart_urls = {}
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Handle system-wide analytics vs user-specific
    folder_prefix = 'system_wide' if user_id == 'all' else user_id
    
    # 1. Sentiment Distribution Pie Chart
    chart_urls['sentiment_pie'] = create_sentiment_pie_chart(data, timestamp, folder_prefix)
    
    # 2. Pain Points Bar Chart
    chart_urls['pain_points'] = create_pain_points_chart(data, timestamp, folder_prefix)
    
    # 3. Top Insights Chart
    chart_urls['insights'] = create_insights_chart(data, timestamp, folder_prefix)
    
    # 4. Response Analytics
    chart_urls['response_analytics'] = create_response_analytics(data, timestamp, folder_prefix)
    
    # 5. Sentiment Trend (if multiple surveys)
    if len(data) > 1:
        chart_urls['sentiment_trend'] = create_sentiment_trend(data, timestamp, folder_prefix)
    
    # 6. Feedback Quality Analysis
    chart_urls['feedback_quality'] = create_feedback_quality_chart(data, timestamp, folder_prefix)
    
    # 7. Comparative Analysis (if multiple surveys)
    if len(data) > 1:
        chart_urls['comparative'] = create_comparative_analysis(data, timestamp, folder_prefix)
    
    return chart_urls
def create_sentiment_pie_chart(data, timestamp,folder_prefix):
    """Create sentiment distribution pie chart"""
    
    # Aggregate sentiment data
    total_positive = sum(float(item.get('sentiment_breakdown', {}).get('positive', 0)) for item in data)
    total_neutral = sum(float(item.get('sentiment_breakdown', {}).get('neutral', 0)) for item in data)
    total_negative = sum(float(item.get('sentiment_breakdown', {}).get('negative', 0)) for item in data)
    
    num_surveys = len(data)
    avg_positive = total_positive / num_surveys if num_surveys > 0 else 0
    avg_neutral = total_neutral / num_surveys if num_surveys > 0 else 0
    avg_negative = total_negative / num_surveys if num_surveys > 0 else 0
    
    # Create pie chart
    fig, ax = plt.subplots(figsize=(10, 8))
    
    labels = ['Positive', 'Neutral', 'Negative']
    sizes = [avg_positive, avg_neutral, avg_negative]
    colors = ['#2E8B57', '#FFD700', '#DC143C']  # Green, Gold, Red
    explode = (0.05, 0.05, 0.05)  # Slight separation
    
    wedges, texts, autotexts = ax.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                     explode=explode, shadow=True, startangle=90)
    
    # Styling
    ax.set_title('Overall Sentiment Distribution\nAcross All Surveys', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Make percentage text bold
    for autotext in autotexts:
        autotext.set_color('white')
        autotext.set_fontweight('bold')
        autotext.set_fontsize(12)
    
    plt.tight_layout()

    # Save to S3
    # return save_chart_to_s3(fig, f'sentiment_distribution_{timestamp}.png')
    filename = f'{folder_prefix}_sentiment_distribution_{timestamp}.png'
    return save_chart_to_s3(fig, filename, folder_prefix)

def create_pain_points_chart(data, timestamp, folder_prefix):
    """Create horizontal bar chart for top pain points"""
    
    # Aggregate all pain points
    all_pain_points = []
    for item in data:
        pain_points = item.get('pain_points', [])
        if isinstance(pain_points, list):
            all_pain_points.extend(pain_points)
    
    # Count frequency
    pain_point_counts = Counter(all_pain_points)
    top_pain_points = pain_point_counts.most_common(10)
    
    if not top_pain_points:
        return None
    
    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    points = [point[0] for point in top_pain_points]
    counts = [point[1] for point in top_pain_points]
    
    # Truncate long text
    points = [point[:50] + '...' if len(point) > 50 else point for point in points]
    
    bars = ax.barh(range(len(points)), counts, color=sns.color_palette("Reds_r", len(points)))
    
    # Styling
    ax.set_yticks(range(len(points)))
    ax.set_yticklabels(points)
    ax.set_xlabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Top 10 Pain Points Mentioned by Students', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    filename = f'{folder_prefix}_pain_points_{timestamp}.png'
    
    return save_chart_to_s3(fig, filename, folder_prefix)

def create_insights_chart(data, timestamp,folder_prefix):
    """Create chart for top actionable insights"""
    
    # Aggregate all insights
    all_insights = []
    for item in data:
        insights = item.get('top_insights', [])
        if isinstance(insights, list):
            all_insights.extend(insights)
    
    # Count frequency
    insight_counts = Counter(all_insights)
    top_insights = insight_counts.most_common(8)
    
    if not top_insights:
        return None
    
    # Create horizontal bar chart
    fig, ax = plt.subplots(figsize=(12, 10))
    
    insights = [insight[0] for insight in top_insights]
    counts = [insight[1] for insight in top_insights]
    
    # Truncate long text
    insights = [insight[:60] + '...' if len(insight) > 60 else insight for insight in insights]
    
    bars = ax.barh(range(len(insights)), counts, color=sns.color_palette("Greens", len(insights)))
    
    # Styling
    ax.set_yticks(range(len(insights)))
    ax.set_yticklabels(insights)
    ax.set_xlabel('Frequency', fontsize=12, fontweight='bold')
    ax.set_title('Top Actionable Insights for Course Improvement', 
                fontsize=16, fontweight='bold', pad=20)
    
    # Add value labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, 
                f'{int(width)}', ha='left', va='center', fontweight='bold')
    
    plt.tight_layout()
    filename = f'{folder_prefix}_top_insights_{timestamp}.png'
    return save_chart_to_s3(fig, filename, folder_prefix)

def create_response_analytics(data, timestamp, folder_prefix):
    """Create response analytics chart"""
    
    # Extract data
    response_counts = [int(item.get('response_count', 0)) for item in data]
    feedback_counts = [int(item.get('feedback_count', 0)) for item in data]
    survey_dates = [item.get('analyzed_at', '')[:10] for item in data]  # Get date part
    
    # Create subplot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Chart 1: Response vs Feedback Count
    x = range(len(data))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], response_counts, width, label='Total Responses', alpha=0.8)
    ax1.bar([i + width/2 for i in x], feedback_counts, width, label='With Feedback', alpha=0.8)
    
    ax1.set_xlabel('Survey Index')
    ax1.set_ylabel('Count')
    ax1.set_title('Response vs Feedback Count by Survey')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Chart 2: Feedback Completion Rate
    completion_rates = [fb/resp*100 if resp > 0 else 0 for fb, resp in zip(feedback_counts, response_counts)]
    
    colors = ['green' if rate >= 70 else 'orange' if rate >= 50 else 'red' for rate in completion_rates]
    bars = ax2.bar(x, completion_rates, color=colors, alpha=0.7)
    
    ax2.set_xlabel('Survey Index')
    ax2.set_ylabel('Completion Rate (%)')
    ax2.set_title('Feedback Completion Rate by Survey')
    ax2.axhline(y=50, color='red', linestyle='--', alpha=0.7, label='50% Threshold')
    ax2.axhline(y=70, color='green', linestyle='--', alpha=0.7, label='70% Target')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Add percentage labels
    for bar, rate in zip(bars, completion_rates):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{rate:.1f}%', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    filename = f'{folder_prefix}_response_analytics_{timestamp}.png'
    return save_chart_to_s3(fig, filename, folder_prefix)

def create_sentiment_trend(data, timestamp,folder_prefix):
    """Create sentiment trend over time"""
    
    # Sort data by date
    sorted_data = sorted(data, key=lambda x: x.get('analyzed_at', ''))
    
    dates = [item.get('analyzed_at', '')[:10] for item in sorted_data]
    positive_scores = [float(item.get('sentiment_breakdown', {}).get('positive', 0)) for item in sorted_data]
    negative_scores = [float(item.get('sentiment_breakdown', {}).get('negative', 0)) for item in sorted_data]
    neutral_scores = [float(item.get('sentiment_breakdown', {}).get('neutral', 0)) for item in sorted_data]
    
    # Create line chart
    fig, ax = plt.subplots(figsize=(12, 8))
    
    x = range(len(dates))
    ax.plot(x, positive_scores, marker='o', linewidth=2, label='Positive', color='green')
    ax.plot(x, negative_scores, marker='s', linewidth=2, label='Negative', color='red')
    ax.plot(x, neutral_scores, marker='^', linewidth=2, label='Neutral', color='orange')
    
    # Styling
    ax.set_xlabel('Survey Timeline', fontsize=12, fontweight='bold')
    ax.set_ylabel('Sentiment Score (%)', fontsize=12, fontweight='bold')
    ax.set_title('Sentiment Trends Over Time', fontsize=16, fontweight='bold', pad=20)
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # Set x-axis labels (showing every few dates to avoid crowding)
    step = max(1, len(dates) // 10)
    ax.set_xticks(range(0, len(dates), step))
    ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=45)
    
    plt.tight_layout()
    filename = f'{folder_prefix}_sentiment_trend_{timestamp}.png'
    return save_chart_to_s3(fig, filename, folder_prefix)

def create_feedback_quality_chart(data, timestamp,folder_prefix):
    """Create feedback quality analysis"""
    
    # Calculate metrics
    total_responses = sum(int(item.get('response_count', 0)) for item in data)
    total_feedback = sum(int(item.get('feedback_count', 0)) for item in data)
    
    # Create donut chart
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
    
    # Donut chart 1: Response Quality
    with_feedback = total_feedback
    without_feedback = total_responses - total_feedback
    
    sizes = [with_feedback, without_feedback]
    labels = ['With Feedback', 'Without Feedback']
    colors = ['#32CD32', '#FF6347']
    
    wedges, texts, autotexts = ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%',
                                      startangle=90, pctdistance=0.85)
    
    # Create donut hole
    centre_circle = plt.Circle((0,0), 0.70, fc='white')
    ax1.add_artist(centre_circle)
    
    ax1.set_title('Overall Response Quality', fontsize=14, fontweight='bold')
    
    # Chart 2: Quality by Survey
    survey_quality = []
    for item in data:
        resp_count = int(item.get('response_count', 0))
        fb_count = int(item.get('feedback_count', 0))
        quality = fb_count / resp_count * 100 if resp_count > 0 else 0
        survey_quality.append(quality)
    
    # Histogram of quality scores
    ax2.hist(survey_quality, bins=10, color='skyblue', alpha=0.7, edgecolor='black')
    ax2.set_xlabel('Feedback Quality (%)')
    ax2.set_ylabel('Number of Surveys')
    ax2.set_title('Distribution of Feedback Quality Across Surveys')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    filename = f'{folder_prefix}_feedback_quality_{timestamp}.png'
    return save_chart_to_s3(fig, filename, folder_prefix)

def create_comparative_analysis(data, timestamp,folder_prefix):
    """Create comparative analysis across surveys"""
    
    # Extract data for comparison
    survey_ids = [f"Survey {i+1}" for i in range(len(data))]
    positive_scores = [float(item.get('sentiment_breakdown', {}).get('positive', 0)) for item in data]
    negative_scores = [float(item.get('sentiment_breakdown', {}).get('negative', 0)) for item in data]
    response_counts = [int(item.get('response_count', 0)) for item in data]
    
    # Create stacked bar chart
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Chart 1: Sentiment Comparison
    x = np.arange(len(survey_ids))
    width = 0.35
    
    ax1.bar(x - width/2, positive_scores, width, label='Positive %', color='green', alpha=0.7)
    ax1.bar(x + width/2, negative_scores, width, label='Negative %', color='red', alpha=0.7)
    
    ax1.set_xlabel('Surveys')
    ax1.set_ylabel('Sentiment Score (%)')
    ax1.set_title('Sentiment Comparison Across Surveys')
    ax1.set_xticks(x)
    ax1.set_xticklabels(survey_ids, rotation=45)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Chart 2: Response Volume
    bars = ax2.bar(x, response_counts, color='steelblue', alpha=0.7)
    ax2.set_xlabel('Surveys')
    ax2.set_ylabel('Number of Responses')
    ax2.set_title('Response Volume Comparison')
    ax2.set_xticks(x)
    ax2.set_xticklabels(survey_ids, rotation=45)
    ax2.grid(True, alpha=0.3)
    
    # Add value labels
    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + max(response_counts)*0.01,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    filename = f'{folder_prefix}_comparative_analysis_{timestamp}.png'
    return save_chart_to_s3(fig, filename, folder_prefix)
def save_chart_to_s3(fig, filename, folder_prefix):
    """Save matplotlib figure to S3 and return URL"""
    
    try:
        # Save figure to bytes buffer
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buffer.seek(0)
        
        # Create user-specific S3 path
        s3_key = f"{VISUALS_PREFIX}{folder_prefix}/{filename}"
        
        # Upload to S3
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=buffer.getvalue(),
            ContentType='image/png',
          #  ACL='public-read'  # Make publicly accessible
        )
        
        # Clean up
        plt.close(fig)
        buffer.close()
        
        # Return S3 URL
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        print(f"Chart saved successfully: {s3_url}")
        
        return s3_url
        
    except Exception as e:
        print(f"Error saving chart to S3: {str(e)}")
        plt.close(fig)
        return None
if __name__ == "__main__":
    args = sys.argv
    user_id = args[args.index('--user_id') + 1] if '--user_id' in args else 'all'
    upload_id = args[args.index('--upload_id') + 1] if '--upload_id' in args else None
    event = {"user_id": user_id, "upload_id": upload_id}
    lambda_handler(event, None)
