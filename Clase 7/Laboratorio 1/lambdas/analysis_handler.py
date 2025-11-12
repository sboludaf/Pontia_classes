import json
import boto3
import os
import numpy as np
from datetime import datetime
from decimal import Decimal

# Initialize AWS clients
rekognition_client = boto3.client('rekognition')
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

# PPE detection configuration
PPE_LABELS = {
    'helmet': {'label': 'Helmet', 'required': True, 'confidence_threshold': 70},
    'vest': {'label': 'Vest', 'required': True, 'confidence_threshold': 70},
    'boots': {'label': 'Boots', 'required': True, 'confidence_threshold': 60},
    'gloves': {'label': 'Gloves', 'required': False, 'confidence_threshold': 60},
    'glasses': {'label': 'Glasses', 'required': False, 'confidence_threshold': 60}
}

SAFETY_HAZARDS = {
    'construction_equipment': {'risk': 'high', 'label': 'Construction Equipment'},
    'scaffold': {'risk': 'medium', 'label': 'Scaffold'},
    'excavation': {'risk': 'high', 'label': 'Excavation'},
    'electrical': {'risk': 'high', 'label': 'Electrical Equipment'},
    'tools': {'risk': 'medium', 'label': 'Power Tools'},
    'debris': {'risk': 'low', 'label': 'Debris'},
    'unprotected_height': {'risk': 'high', 'label': 'Unprotected Height'}
}

def lambda_handler(event, context):
    """
    Lambda function to analyze images for PPE and safety hazards using Rekognition
    """
    try:
        print(f"🔍 Starting safety analysis...")
        
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
        
        # Parse input
        if 'image_id' in event and 's3_key' in event:
            # Triggered from upload function
            image_id = event['image_id']
            s3_key = event['s3_key']
        else:
            # Direct API call
            if isinstance(event.get('body'), str):
                body = json.loads(event['body'])
            else:
                body = event['body']
            
            image_id = body.get('image_id')
            s3_key = body.get('s3_key')
        
        if not image_id or not s3_key:
            return error_response(400, "Missing image_id or s3_key")
        
        print(f"📸 Analyzing image: {image_id} from {s3_key}")
        
        # Get existing analysis record
        try:
            response = analysis_table.get_item(Key={'image_id': image_id, 'timestamp': 'latest'})
            if 'Item' in response:
                analysis_record = response['Item']
            else:
                return error_response(404, f"Analysis record not found for image {image_id}")
        except Exception as e:
            return error_response(500, f"Error retrieving analysis record: {str(e)}")
        
        # Perform Rekognition analysis
        try:
            analysis_result = analyze_image_with_rekognition(s3_key)
            print(f"✅ Rekognition analysis completed")
            
        except Exception as e:
            print(f"❌ Rekognition analysis failed: {str(e)}")
            # Update record with error
            analysis_record['status'] = 'analysis_failed'
            analysis_record['error'] = str(e)
            analysis_record['analyzed_at'] = datetime.now().isoformat()
            analysis_table.put_item(Item=analysis_record)
            return error_response(500, f"Analysis failed: {str(e)}")
        
        # Process analysis results
        try:
            ppe_detected, safety_score, violations = process_analysis_results(analysis_result)
            print(f"✅ Analysis processed: Score={safety_score}, Violations={len(violations)}")
            
        except Exception as e:
            print(f"❌ Error processing results: {str(e)}")
            return error_response(500, f"Error processing analysis: {str(e)}")
        
        # Update analysis record
        try:
            analysis_record.update({
                'status': 'analyzed',
                'analysis_result': analysis_result,
                'ppe_detected': ppe_detected,
                'safety_score': safety_score,
                'violations': violations,
                'analyzed_at': datetime.now().isoformat()
            })
            
            # Convert Decimal values for DynamoDB
            analysis_record = convert_decimals(analysis_record)
            analysis_table.put_item(Item=analysis_record)
            print(f"✅ Analysis record updated")
            
        except Exception as e:
            print(f"❌ Error updating analysis record: {str(e)}")
            return error_response(500, f"Error updating record: {str(e)}")
        
        # Update site statistics
        try:
            update_site_statistics(analysis_record['site_id'], safety_score, len(violations))
            print(f"✅ Site statistics updated")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not update statistics: {str(e)}")
        
        # Send notification if violations detected
        if violations:
            try:
                send_safety_alert(analysis_record, violations)
                print(f"🚨 Safety alert sent")
            except Exception as e:
                print(f"⚠️ Warning: Could not send alert: {str(e)}")
        
        # Return analysis results
        response_data = {
            'image_id': image_id,
            'analysis_completed': True,
            'safety_score': safety_score,
            'ppe_detected': ppe_detected,
            'violations': violations,
            'analysis_timestamp': datetime.now().isoformat(),
            'site_id': analysis_record['site_id'],
            'location': analysis_record.get('location', 'unknown')
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token,X-Requested-With',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps(response_data, default=str)
        }
        
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return error_response(500, f"Internal server error: {str(e)}")

def analyze_image_with_rekognition(s3_key):
    """
    Analyze image using Amazon Rekognition for PPE and hazards
    """
    analysis_result = {}
    
    # 1. Detect general labels
    try:
        labels_response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': IMAGES_BUCKET, 'Name': s3_key}},
            MaxLabels=50,
            MinConfidence=50
        )
        analysis_result['labels'] = labels_response['Labels']
        print(f"📋 Detected {len(labels_response['Labels'])} labels")
        
    except Exception as e:
        print(f"❌ Error detecting labels: {str(e)}")
        analysis_result['labels'] = []
    
    # 2. Detect protective equipment
    try:
        ppe_response = rekognition_client.detect_protective_equipment(
            Image={'S3Object': {'Bucket': IMAGES_BUCKET, 'Name': s3_key}},
            SummarizationAttributes={'MinConfidence': 50, 'RequiredEquipmentTypes': ['FACE_COVER', 'HEAD_COVER', 'HAND_COVER']}
        )
        analysis_result['protective_equipment'] = ppe_response
        print(f"🛡️ PPE analysis completed")
        
    except Exception as e:
        print(f"❌ Error detecting PPE: {str(e)}")
        analysis_result['protective_equipment'] = {}
    
    # 3. Detect people (for PPE compliance per person)
    try:
        people_response = rekognition_client.detect_labels(
            Image={'S3Object': {'Bucket': IMAGES_BUCKET, 'Name': s3_key}},
            MaxLabels=10,
            MinConfidence=70
        )
        
        # Count people detected
        people_count = sum(1 for label in people_response['Labels'] 
                          if label['Name'].lower() in ['person', 'people'])
        analysis_result['people_count'] = people_count
        print(f"👥 Detected {people_count} people")
        
    except Exception as e:
        print(f"❌ Error detecting people: {str(e)}")
        analysis_result['people_count'] = 0
    
    return analysis_result

def process_analysis_results(analysis_result):
    """
    Process Rekognition results to extract PPE compliance and safety score
    """
    ppe_detected = {}
    violations = []
    
    # Process PPE detection
    if 'protective_equipment' in analysis_result and 'Persons' in analysis_result['protective_equipment']:
        persons = analysis_result['protective_equipment']['Persons']
        
        for person_idx, person in enumerate(persons):
            person_ppe = {}
            person_violations = []
            
            # Check body parts for PPE
            if 'BodyParts' in person:
                for body_part in person['BodyParts']:
                    name = body_part.get('Name', '').lower()
                    
                    if 'head' in name:
                        # Check for helmet/head cover
                        if 'EquipmentDetections' in body_part:
                            has_helmet = any(eq['Type'] == 'HEAD_COVER' 
                                           and eq['CoversBodyPart']['Confidence'] > 70 
                                           for eq in body_part['EquipmentDetections'])
                            person_ppe['helmet'] = has_helmet
                            if not has_helmet:
                                person_violations.append('No helmet detected')
                    
                    elif 'face' in name:
                        # Check for face cover/glasses
                        if 'EquipmentDetections' in body_part:
                            has_glasses = any(eq['Type'] == 'FACE_COVER' 
                                            and eq['CoversBodyPart']['Confidence'] > 60 
                                            for eq in body_part['EquipmentDetections'])
                            person_ppe['glasses'] = has_glasses
                    
                    elif 'hand' in name or 'arm' in name:
                        # Check for gloves
                        if 'EquipmentDetections' in body_part:
                            has_gloves = any(eq['Type'] == 'HAND_COVER' 
                                           and eq['CoversBodyPart']['Confidence'] > 60 
                                           for eq in body_part['EquipmentDetections'])
                            person_ppe['gloves'] = has_gloves
                            if not has_gloves:
                                person_violations.append('No gloves detected')
            
            ppe_detected[f'person_{person_idx + 1}'] = person_ppe
            violations.extend([f"Person {person_idx + 1}: {violation}" for violation in person_violations])
    
    # Process general labels for safety hazards
    if 'labels' in analysis_result:
        detected_labels = [label['Name'].lower() for label in analysis_result['labels']]
        
        for hazard_key, hazard_config in SAFETY_HAZARDS.items():
            if hazard_key in detected_labels or any(hazard_key in label for label in detected_labels):
                violations.append(f"Safety hazard detected: {hazard_config['label']}")
    
    # Calculate safety score (0-100)
    total_required_items = sum(1 for ppe in PPE_LABELS.values() if ppe['required'])
    detected_required = 0
    
    for person_ppe in ppe_detected.values():
        person_score = 0
        for ppe_key, ppe_config in PPE_LABELS.items():
            if ppe_config['required'] and person_ppe.get(ppe_key, False):
                person_score += 1
        detected_required = max(detected_required, person_score)
    
    if total_required_items > 0:
        base_score = (detected_required / total_required_items) * 100
    else:
        base_score = 100
    
    # Deduct points for hazards
    hazard_deduction = min(len([v for v in violations if 'hazard' in v.lower()]) * 10, 50)
    safety_score = max(0, base_score - hazard_deduction)
    
    return ppe_detected, int(safety_score), violations

def update_site_statistics(site_id, safety_score, violation_count):
    """
    Update site statistics with analysis results
    """
    date_key = datetime.now().strftime('%Y-%m-%d')
    
    try:
        # Get current stats
        response = stats_table.get_item(
            Key={'site_id': site_id, 'date': date_key}
        )
        
        if 'Item' in response:
            stats = response['Item']
        else:
            # Initialize stats
            stats = {
                'site_id': site_id,
                'date': date_key,
                'total_images': 0,
                'analyzed_images': 0,
                'violations_detected': 0,
                'avg_safety_score': 0,
                'created_at': datetime.now().isoformat()
            }
        
        # Update statistics
        stats['analyzed_images'] += 1
        
        # Update average safety score
        current_avg = stats.get('avg_safety_score', 0)
        analyzed_count = stats['analyzed_images']
        stats['avg_safety_score'] = ((current_avg * (analyzed_count - 1)) + safety_score) / analyzed_count
        
        stats['violations_detected'] += violation_count
        stats['last_updated'] = datetime.now().isoformat()
        
        # Save updated stats
        stats_table.put_item(Item=convert_decimals(stats))
        
    except Exception as e:
        print(f"Error updating statistics: {str(e)}")
        raise

def send_safety_alert(analysis_record, violations):
    """
    Send safety alert notification (placeholder for SNS implementation)
    """
    # This would integrate with SNS to send alerts
    # For now, just log the alert
    alert_message = f"""
    🚨 SAFETY ALERT 🚨
    Site: {analysis_record['site_id']}
    Location: {analysis_record.get('location', 'unknown')}
    Image ID: {analysis_record['image_id']}
    Safety Score: {analysis_record['safety_score']}
    Violations: {len(violations)}
    
    Violations detected:
    {chr(10).join(f"- {violation}" for violation in violations)}
    """
    
    print(alert_message)
    
    # TODO: Implement SNS notification
    # sns_client.publish(
    #     TopicArn=os.environ['SNS_TOPIC_ARN'],
    #     Subject=f"Safety Alert - {analysis_record['site_id']}",
    #     Message=alert_message
    # )

def convert_decimals(obj):
    """
    Convert Decimal objects to float for JSON serialization
    """
    if isinstance(obj, list):
        return [convert_decimals(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: convert_decimals(value) for key, value in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    else:
        return obj

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
