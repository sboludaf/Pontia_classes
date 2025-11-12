import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
sns = boto3.client('sns')

table = dynamodb.Table(os.environ['SUBSCRIBERS_TABLE'])
topic_arn = os.environ['SNS_TOPIC_ARN']

def lambda_handler(event, context):
    # Manejar preflight OPTIONS
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': ''
        }

    try:
        body = json.loads(event.get('body', '{}'))
        subject = body.get('subject', '').strip()
        message = body.get('message', '').strip()
        admin_key = body.get('admin_key', '').strip()

        if admin_key != 'admin-secret-key-123':
            return {
                'statusCode': 403,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'No autorizado'})
            }

        if not subject or not message:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Asunto y mensaje son requeridos'})
            }

        response = table.scan(
            FilterExpression='confirmed = :confirmed',
            ExpressionAttributeValues={':confirmed': True}
        )

        confirmed_count = len(response.get('Items', []))

        formatted_message = f"{message}\n\n---\nEnviado: {datetime.utcnow().isoformat()}"

        sns.publish(
            TopicArn=topic_arn,
            Subject=subject,
            Message=formatted_message
        )

        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': '¡Mensaje Enviado!',
                'count': confirmed_count
            })
        }

    except Exception as e:
        print(f'Error: {str(e)}')
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'error': f'Error interno: {str(e)}'})
        }
