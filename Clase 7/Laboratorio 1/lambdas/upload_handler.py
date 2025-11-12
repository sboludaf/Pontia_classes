import json
import uuid
import boto3
import os
from datetime import datetime
from urllib.parse import unquote_plus

# Initialize AWS clients
s3_client = boto3.client('s3')
dynamodb_client = boto3.resource('dynamodb')

# Environment variables
IMAGES_BUCKET = os.environ['IMAGES_BUCKET']
ANALYSIS_TABLE = os.environ['ANALYSIS_TABLE']
STATS_TABLE = os.environ['STATS_TABLE']
REGION = os.environ['REGION']

# DynamoDB tables
analysis_table = dynamodb_client.Table(ANALYSIS_TABLE)
stats_table = dynamodb_client.Table(STATS_TABLE)

def lambda_handler(event, context):
    """
    Lambda function to handle image uploads for safety analysis
    """
    try:
        print(f"📸 Processing upload request...")
        
        # Handle CORS preflight request
        if event.get("httpMethod") == "OPTIONS":
            print("Handling OPTIONS request")
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token,X-Requested-With",
                    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                },
                "body": json.dumps({"message": "CORS preflight"})
            }
        
        # Parse the request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event['body']
        
        # Extract image data and metadata
        image_data = body.get('image_data')
        site_id = body.get('site_id', 'unknown')
        location = body.get('location', 'unknown')
        timestamp = body.get('timestamp', datetime.now().isoformat())
        
        if not image_data:
            return error_response(400, "Missing image_data in request")
        
        # Generate unique image ID
        image_id = str(uuid.uuid4())
        
        # Decode and upload image to S3
        try:
            import base64
            image_bytes = base64.b64decode(image_data)
            
            # Upload to S3
            s3_key = f"images/{site_id}/{image_id}.jpg"
            s3_client.put_object(
                Bucket=IMAGES_BUCKET,
                Key=s3_key,
                Body=image_bytes,
                ContentType='image/jpeg',
                Metadata={
                    'site_id': site_id,
                    'location': location,
                    'upload_timestamp': timestamp,
                    'image_id': image_id
                }
            )
            
            print(f"✅ Image uploaded to S3: {s3_key}")
            
        except Exception as e:
            print(f"❌ Error uploading to S3: {str(e)}")
            return error_response(500, f"Error uploading image: {str(e)}")
        
        # Save analysis record to DynamoDB
        try:
            analysis_record = {
                'image_id': image_id,
                'timestamp': timestamp,
                'site_id': site_id,
                'location': location,
                's3_key': s3_key,
                'status': 'uploaded',
                'analysis_result': None,
                'ppe_detected': {},
                'safety_score': 0,
                'violations': [],
                'created_at': datetime.now().isoformat()
            }
            
            analysis_table.put_item(Item=analysis_record)
            print(f"✅ Analysis record saved to DynamoDB")
            
        except Exception as e:
            print(f"❌ Error saving to DynamoDB: {str(e)}")
            return error_response(500, f"Error saving analysis record: {str(e)}")
        
        # Update site statistics
        try:
            update_site_stats(site_id, 'uploaded')
            print(f"✅ Site statistics updated")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not update stats: {str(e)}")
        
        # Trigger analysis (optional - could be async)
        try:
            trigger_analysis(image_id, s3_key)
            print(f"✅ Analysis triggered for image {image_id}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not trigger analysis: {str(e)}")
        
        # Return success response
        response_data = {
            'image_id': image_id,
            's3_key': s3_key,
            'status': 'uploaded',
            'message': 'Image uploaded successfully',
            'upload_timestamp': timestamp,
            'site_id': site_id,
            'location': location
        }
        
        return success_response(200, response_data)
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return error_response(500, f"Internal server error: {str(e)}")

def trigger_analysis(image_id, s3_key):
    """
    Trigger analysis of the uploaded image
    """
    import boto3
    
    lambda_client = boto3.client('lambda')
    
    # Call analysis function
    payload = {
        'image_id': image_id,
        's3_key': s3_key,
        'trigger_source': 'upload'
    }
    
    lambda_client.invoke(
        FunctionName=os.environ['AWS_LAMBDA_FUNCTION_NAME'].replace('upload', 'analyze'),
        InvocationType='Event',  # Async invocation
        Payload=json.dumps(payload)
    )

def update_site_stats(site_id, action):
    """
    Update site statistics in DynamoDB
    """
    date_key = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Get current stats
        response = stats_table.get_item(
            Key={
                'site_id': site_id,
                'date': date_key
            }
        )
        
        if 'Item' in response:
            stats = response['Item']
        else:
            # Initialize stats for new day
            stats = {
                'site_id': site_id,
                'date': date_key,
                'total_images': 0,
                'analyzed_images': 0,
                'violations_detected': 0,
                'avg_safety_score': 0,
                'created_at': datetime.now().isoformat()
            }
        
        # Update stats
        stats['total_images'] += 1
        stats['last_updated'] = datetime.now().isoformat()
        
        # Save updated stats
        stats_table.put_item(Item=stats)
        
    except Exception as e:
        print(f"Error updating stats: {str(e)}")
        raise

def success_response(status_code, data):
    """Return success response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token,X-Requested-With',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data, default=str)
    }

def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token,X-Requested-With',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({'error': message})
    }
