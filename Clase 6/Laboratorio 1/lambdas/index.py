"""
Index Router Lambda
Enruta requests a los handlers apropiados según el método HTTP
"""

import json
import os


def lambda_handler(event, context):
    """
    Router principal que dirige a los handlers específicos
    
    - Para /upload y /documents -> upload_handler
    - Para /query -> query_handler
    """
    
    print(f"Router Event: {json.dumps(event)}")
    print(f"Path: {event.get('path', '')}")
    print(f"HTTP Method: {event.get('httpMethod', '')}")
    
    # Determinar el handler basado en el path
    path = event.get('path', '')
    
    if path.endswith('/upload') or path.endswith('/documents'):
        print("Enviando a upload_handler")
        # Importar solo cuando se necesita
        from upload_handler import lambda_handler as upload_handler
        return upload_handler(event, context)
    elif path.endswith('/query'):
        print("Enviando a query_handler")
        # Importar solo cuando se necesita
        from query_handler import lambda_handler as query_handler
        return query_handler(event, context)
    else:
        print("Path no reconocido")
        return {
            "statusCode": 404,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type,Authorization,X-Amz-Date,X-Amz-Security-Token",
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            },
            "body": json.dumps({"error": f"Path no encontrado: {path}"}),
        }
