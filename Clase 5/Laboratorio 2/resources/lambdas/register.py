import json
import boto3
import os
from datetime import datetime
import uuid

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
        email = body.get('email', '').strip()
        name = body.get('name', '').strip()

        if not email or not name:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Email y nombre son requeridos'})
            }

        response = table.get_item(Key={'email': email})
        if 'Item' in response:
            return {
                'statusCode': 409,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'El email ya está registrado'})
            }

        confirmation_token = str(uuid.uuid4())

        table.put_item(
            Item={
                'email': email,
                'name': name,
                'confirmed': False,
                'confirmation_token': confirmation_token,
                'created_at': datetime.utcnow().isoformat(),
                'subscription_arn': None
            }
        )

        sub_response = sns.subscribe(
            TopicArn=topic_arn,
            Protocol='email',
            Endpoint=email,
            Attributes={'FilterPolicy': json.dumps({})}
        )

        table.update_item(
            Key={'email': email},
            UpdateExpression='SET subscription_arn = :arn',
            ExpressionAttributeValues={':arn': sub_response['SubscriptionArn']}
        )

        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({
                'message': 'Usuario registrado. Por favor confirma tu suscripción en tu email',
                'email': email
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
