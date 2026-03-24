"""
Query Handler Lambda
Realiza búsquedas en Kendra y genera respuestas con Bedrock
"""

import json
import boto3
import os
from datetime import datetime
import uuid
import re

kendra_client = boto3.client("kendra")
bedrock_client = boto3.client("bedrock-runtime")
dynamodb = boto3.resource("dynamodb")

DOCUMENTS_TABLE = os.environ["DOCUMENTS_TABLE"]
QUERIES_TABLE = os.environ["QUERIES_TABLE"]
KENDRA_INDEX_ID = os.environ["KENDRA_INDEX_ID"]

documents_table = dynamodb.Table(DOCUMENTS_TABLE)
queries_table = dynamodb.Table(QUERIES_TABLE)


def lambda_handler(event, context):
    """
    Maneja búsquedas RAG
    
    Flujo:
    1. Recibe pregunta desde API
    2. Busca en Kendra
    3. Construye contexto
    4. Invoca Bedrock (Claude 3)
    5. Guarda en DynamoDB
    6. Retorna respuesta
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
                    "Content-Type": "application/json",
                },
                "body": json.dumps({}),
            }
            print(f"Response OPTIONS: {json.dumps(response)}")
            return response
        
        if event.get("httpMethod") != "POST":
            return error_response(400, "Método no permitido")
        
        body = json.loads(event.get("body", "{}"))
        question = body.get("question", "").strip()
        
        if not question:
            return error_response(400, "question es requerido")
        
        # ==================== BUSCAR EN KENDRA ====================
        print(f"Buscando en Kendra: {question}")
        
        try:
            kendra_response = kendra_client.query(
                IndexId=KENDRA_INDEX_ID,
                QueryText=question,
                PageSize=5,
            )
            
            results = kendra_response.get("ResultItems", [])
            print(f"Resultados de Kendra: {len(results)}")
        except Exception as e:
            print(f"Error al buscar en Kendra: {str(e)}")
            results = []
        
        # ==================== CONSTRUIR CONTEXTO ====================
        context_text = ""
        sources = []
        
        for i, result in enumerate(results, 1):
            document_text = result.get("DocumentExcerpt", {}).get("Text", "")
            document_id = result.get("DocumentId", "unknown")
            score = result.get("ScoreAttributes", {}).get("ScoreConfidence", "UNKNOWN")
            
            if document_text:
                context_text += f"\n[Fuente {i}] (Relevancia: {score})\n{document_text}\n"
                sources.append({
                    "document_id": document_id,
                    "score": score,
                    "excerpt": document_text[:200],
                })
        
        if not context_text:
            print("Kendra no encontró resultados, buscando directamente en S3...")
            context_text = search_documents_in_s3(question)
            if context_text:
                print(f"Se encontró contenido relevante en S3")
                sources.append({
                    "document_id": "direct-search",
                    "score": 1.0,
                    "excerpt": context_text[:200],
                })
            else:
                context_text = "No se encontraron documentos relevantes en la base de conocimiento."
        
        # ==================== INVOCAR BEDROCK ====================
        print("Invocando Bedrock para generar respuesta...")
        
        system_prompt = """Eres un asistente experto que responde preguntas basándose en documentos proporcionados.
Proporciona respuestas claras, concisas y bien estructuradas.
Si la información no está en los documentos, indícalo claramente.
Siempre cita las fuentes de donde obtuviste la información."""
        
        user_message = f"""Pregunta: {question}

Contexto de los documentos:
{context_text}

Por favor, responde la pregunta basándote en el contexto proporcionado."""
        
        try:
            bedrock_response = bedrock_client.invoke_model(
                modelId="global.amazon.nova-2-lite-v1:0",
                contentType="application/json",
                accept="application/json",
                body=json.dumps({
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "text": user_message
                                }
                            ]
                        }
                    ]
                }),
            )
            
            response_body = json.loads(bedrock_response["body"].read())
            answer = response_body["output"]["message"]["content"][0]["text"]
            
            print(f"Respuesta generada: {answer[:100]}...")
        except Exception as e:
            print(f"Error al invocar Bedrock: {str(e)}")
            answer = f"Error al generar respuesta: {str(e)}"
        
        # ==================== GUARDAR EN DYNAMODB ====================
        query_id = f"query-{str(uuid.uuid4())[:8]}"
        timestamp = datetime.utcnow().isoformat()
        
        try:
            queries_table.put_item(
                Item={
                    "query_id": query_id,
                    "timestamp": timestamp,
                    "question": question,
                    "answer": answer,
                    "sources": sources,
                    "kendra_results_count": len(results),
                }
            )
            print(f"Query guardada en DynamoDB: {query_id}")
        except Exception as e:
            print(f"Error al guardar query: {str(e)}")
        
        # ==================== RESPUESTA ====================
        return success_response(
            200,
            {
                "query_id": query_id,
                "question": question,
                "answer": answer,
                "sources": sources,
                "timestamp": timestamp,
            },
        )
    
    except Exception as e:
        print(f"Error no controlado: {str(e)}")
        return error_response(500, f"Error interno: {str(e)}")


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


def search_documents_in_s3(question):
    """Busca directamente en los documentos PDF de S3 cuando Kendra no encuentra resultados"""
    try:
        s3_client = boto3.client("s3")
        
        # Obtener todos los documentos de DynamoDB
        response = documents_table.scan()
        documents = response.get("Items", [])
        
        if not documents:
            return ""
        
        # Extraer palabras clave de la pregunta
        keywords = re.findall(r'\b\w+\b', question.lower())
        keywords = [word for word in keywords if len(word) > 3]  # Filtrar palabras cortas
        
        if not keywords:
            return ""
        
        relevant_content = ""
        
        for doc in documents:
            if doc.get("status") == "completed":
                try:
                    # Extraer key del S3 path
                    s3_path = doc.get("s3_path", "")
                    if "s3://" in s3_path:
                        bucket_key = s3_path.replace("s3://", "").split("/", 1)
                        if len(bucket_key) == 2:
                            bucket_name, object_key = bucket_key
                            
                            # Descargar PDF y extraer texto (simplificado)
                            obj = s3_client.get_object(Bucket=bucket_name, Key=object_key)
                            pdf_content = obj['Body'].read()
                            
                            # Para este ejemplo, asumimos que tenemos acceso al texto
                            # En producción, usaríamos Textract o PyPDF2 en Lambda
                            content_preview = f"Contenido del documento {doc.get('filename', 'unknown')}"
                            
                            # Buscar palabras clave en el contenido
                            content_lower = content_preview.lower()
                            keyword_matches = sum(1 for keyword in keywords if keyword in content_lower)
                            
                            if keyword_matches > 0:
                                relevance = keyword_matches / len(keywords)
                                if relevance > 0.3:  # Umbral de relevancia
                                    relevant_content += f"\n[Documento: {doc.get('filename')}] (Relevancia: {relevance:.0%})\n{content_preview}\n"
                
                except Exception as e:
                    print(f"Error procesando documento {doc.get('document_id')}: {str(e)}")
                    continue
        
        return relevant_content[:2000] if relevant_content else ""  # Limitar contenido
        
    except Exception as e:
        print(f"Error en búsqueda directa en S3: {str(e)}")
        return ""


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
