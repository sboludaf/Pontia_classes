import json
import boto3
import base64
import os
from datetime import datetime
from urllib.parse import unquote_plus

# Initialize AWS clients
rekognition = boto3.client('rekognition')
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Environment variables
S3_BUCKET = os.environ.get('S3_BUCKET', 'seguridad-obra-lab')
DYNAMODB_TABLE = os.environ.get('DYNAMODB_TABLE', 'seguridad-analisis')

def lambda_handler(event, context):
    """
    Lambda function to analyze safety equipment in images using AWS Rekognition
    """
    try:
        print(f"Received event: {json.dumps(event)}")
        
        # Parse request body
        if 'body' in event:
            body = json.loads(event['body'])
        else:
            body = event
            
        # Get image data and filename
        image_data = body.get('image')
        filename = body.get('filename', f'image_{datetime.now().timestamp()}.jpg')
        
        if not image_data:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No image data provided'})
            }
        
        # Decode base64 image
        try:
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            print(f"Error decoding base64 image: {str(e)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid image data format'})
            }
        
        # Upload image to S3
        s3_key = f"uploads/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
        try:
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=s3_key,
                Body=image_bytes,
                ContentType='image/jpeg'
            )
            print(f"Image uploaded to S3: s3://{S3_BUCKET}/{s3_key}")
        except Exception as e:
            print(f"Error uploading to S3: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Failed to upload image to S3'})
            }
        
        # Analyze image with Rekognition
        try:
            response = rekognition.detect_labels(
                Image={'Bytes': image_bytes},
                MaxLabels=20,
                MinConfidence=70
            )
            print(f"Rekognition detected {len(response['Labels'])} labels")
        except Exception as e:
            print(f"Error calling Rekognition: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Failed to analyze image with Rekognition'})
            }
        
        # Process analysis results
        analysis_result = process_analysis_results(response, filename, s3_key)
        
        # Save to DynamoDB
        try:
            table = dynamodb.Table(DYNAMODB_TABLE)
            table.put_item(Item=analysis_result)
            print(f"Results saved to DynamoDB: {analysis_result['imageId']}")
        except Exception as e:
            print(f"Error saving to DynamoDB: {str(e)}")
            # Continue even if DynamoDB fails
        
        # Return response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'imageId': analysis_result['imageId'],
                'timestamp': analysis_result['timestamp'],
                'compliance': analysis_result['compliance'],
                'safetyItems': analysis_result['safetyItems'],
                'labels': analysis_result['labels'],
                's3Url': f"s3://{S3_BUCKET}/{s3_key}"
            })
        }
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def process_analysis_results(rekognition_response, filename, s3_key):
    """
    Process Rekognition results to determine safety compliance
    """
    labels = rekognition_response.get('Labels', [])
    detected_labels = [label['Name'] for label in labels]
    
    # Safety equipment detection
    safety_items = {
        'helmet': any(item in detected_labels for item in ['Helmet', 'Hardhat', 'Hard Hat']),
        'glasses': any(item in detected_labels for item in ['Safety Glasses', 'Goggles', 'Eyewear']),
        'gloves': any(item in detected_labels for item in ['Glove', 'Gloves', 'Safety Gloves']),
        'vest': any(item in detected_labels for item in ['Vest', 'Safety Vest', 'Reflective Vest', 'Lifejacket']),
        'footwear': any(item in detected_labels for item in ['Footwear', 'Safety Boots', 'Steel Toe Boots'])
    }
    
    # Calculate compliance score (mandatory items: helmet, glasses, gloves)
    mandatory_items = ['helmet', 'glasses', 'gloves']
    compliance_score = sum(safety_items[item] for item in mandatory_items)
    compliance_percentage = (compliance_score / len(mandatory_items)) * 100
    
    # Determine compliance status
    if compliance_percentage == 100:
        compliance_status = 'CUMPLE NORMATIVA'
        compliance_level = 'high'
    elif compliance_percentage >= 67:
        compliance_status = 'INCUMPLIMIENTO MODERADO'
        compliance_level = 'medium'
    elif compliance_percentage >= 33:
        compliance_status = 'INCUMPLIMIENTO MODERADO'
        compliance_level = 'medium'
    else:
        compliance_status = 'ALTO RIESGO - INCUMPLIMIENTO GRAVE'
        compliance_level = 'low'
    
    # Create analysis result
    image_id = f"img_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename.split('.')[0]}"
    
    return {
        'imageId': image_id,
        'timestamp': datetime.now().isoformat(),
        'filename': filename,
        's3Key': s3_key,
        'compliance': {
            'score': int(compliance_percentage),
            'status': compliance_status,
            'level': compliance_level
        },
        'safetyItems': safety_items,
        'labels': [
            {
                'name': label['Name'],
                'confidence': label['Confidence']
            } for label in labels
        ],
        'detectedLabels': detected_labels,
        'totalLabels': len(labels)
    }
