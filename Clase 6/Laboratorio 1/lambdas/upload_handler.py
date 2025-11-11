"""
Upload Handler Lambda
Procesa la subida de documentos PDF
"""

import json
import boto3
import os
from datetime import datetime
import uuid
from decimal import Decimal

s3_client = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")
kendra_client = boto3.client("kendra")

DOCUMENTS_BUCKET = os.environ["DOCUMENTS_BUCKET"]
DOCUMENTS_TABLE = os.environ["DOCUMENTS_TABLE"]
KENDRA_INDEX_ID = os.environ["KENDRA_INDEX_ID"]

documents_table = dynamodb.Table(DOCUMENTS_TABLE)


def lambda_handler(event, context):
    """
    Maneja la subida de documentos PDF
    
    Flujo:
    1. Recibe PDF desde API
    2. Guarda en S3
    3. Registra en DynamoDB
    4. Dispara sincronización de Kendra
    """
    
    print(f"Event: {json.dumps(event)}")
    print(f"Headers recibidos: {event.get('headers', {})}")
    
    try:
        # ==================== PARSE REQUEST ====================
        if event.get("httpMethod") == "OPTIONS":
            print("Manejando request OPTIONS")
            response = {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token",
                    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
                },
                "body": "",
            }
            print(f"Response OPTIONS: {json.dumps(response)}")
            return response
        
        if event.get("httpMethod") == "GET":
            # Listar documentos
            return list_documents()
        
        if event.get("httpMethod") != "POST":
            return error_response(400, "Método no permitido")
        
        # ==================== EXTRAER DATOS ====================
        body = json.loads(event.get("body", "{}"))
        filename = body.get("filename", "").strip()
        file_content = body.get("file_content", "").strip()
        
        if not filename or not file_content:
            return error_response(400, "filename y file_content son requeridos")
        
        # ==================== GENERAR DOCUMENT ID ====================
        document_id = f"doc-{str(uuid.uuid4())[:8]}"
        
        # ==================== GUARDAR EN S3 ====================
        s3_key = f"documents/{document_id}/{filename}"
        
        try:
            s3_client.put_object(
                Bucket=DOCUMENTS_BUCKET,
                Key=s3_key,
                Body=file_content.encode("utf-8"),
                ContentType="application/pdf",
            )
            print(f"Documento guardado en S3: {s3_key}")
        except Exception as e:
            print(f"Error al guardar en S3: {str(e)}")
            return error_response(500, f"Error al guardar documento: {str(e)}")
        
        # ==================== REGISTRAR EN DYNAMODB ====================
        try:
            documents_table.put_item(
                Item={
                    "document_id": document_id,
                    "filename": filename,
                    "upload_date": datetime.utcnow().isoformat(),
                    "s3_path": f"s3://{DOCUMENTS_BUCKET}/{s3_key}",
                    "status": "processing",
                    "kendra_status": "pending",
                    "metadata": {
                        "size_bytes": len(file_content),
                        "upload_timestamp": datetime.utcnow().isoformat(),
                    },
                }
            )
            print(f"Documento registrado en DynamoDB: {document_id}")
        except Exception as e:
            print(f"Error al registrar en DynamoDB: {str(e)}")
            return error_response(500, f"Error al registrar documento: {str(e)}")
        
        # ==================== DISPARAR SINCRONIZACIÓN KENDRA ====================
        try:
            # Nota: En producción, usar una Lambda async o Step Functions
            # Por ahora solo registramos que necesita sincronización
            print(f"Documento listo para indexación en Kendra: {document_id}")
        except Exception as e:
            print(f"Error al disparar sincronización: {str(e)}")
        
        # ==================== RESPUESTA ====================
        return success_response(
            201,
            {
                "message": "Documento subido exitosamente",
                "document_id": document_id,
                "filename": filename,
                "status": "processing",
            },
        )
    
    except Exception as e:
        print(f"Error no controlado: {str(e)}")
        return error_response(500, f"Error interno: {str(e)}")


def decimal_to_obj(obj):
    """Convierte Decimal a tipos nativos de Python para JSON serialization"""
    if isinstance(obj, list):
        return [decimal_to_obj(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_obj(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        else:
            return float(obj)
    else:
        return obj


def list_documents():
    """Lista todos los documentos"""
    try:
        response = documents_table.scan()
        items = response.get("Items", [])
        
        # Convertir Decimal a tipos nativos
        items = decimal_to_obj(items)
        
        return success_response(200, {"documents": items, "count": len(items)})
    except Exception as e:
        print(f"Error al listar documentos: {str(e)}")
        return error_response(500, f"Error al listar documentos: {str(e)}")


def success_response(status_code, body):
    """Retorna respuesta exitosa"""
    response = {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body),
    }
    print(f"Response success: {json.dumps(response)}")
    return response


def error_response(status_code, message):
    """Retorna respuesta de error"""
    response = {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps({"error": message}),
    }
    print(f"Response error: {json.dumps(response)}")
    return response
