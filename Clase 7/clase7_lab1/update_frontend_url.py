#!/usr/bin/env python3
"""
Script para actualizar la URL del API en el frontend después del despliegue
Uso: python3 update_frontend_url.py [--api-url URL] [--bucket BUCKET] [--region REGION]
"""

import os
import sys
import boto3
import json
import argparse

def get_stack_outputs(stack_name, region):
    """Obtener los outputs del stack de CloudFormation"""
    cf = boto3.client('cloudformation', region_name=region)
    
    try:
        response = cf.describe_stacks(StackName=stack_name)
        stack = response['Stacks'][0]
        
        outputs = {}
        for output in stack.get('Outputs', []):
            outputs[output['OutputKey']] = output['OutputValue']
        
        return outputs
    except Exception as e:
        print(f"❌ Error obteniendo outputs del stack: {e}")
        return None

def update_frontend_url(api_url, frontend_bucket, region):
    """Actualizar app.js localmente y subirlo al bucket S3"""
    s3 = boto3.client('s3', region_name=region)
    
    try:
        # Leer app.js local
        print(f"📝 Leyendo archivo local frontend/app.js...")
        with open("frontend/app.js", "r") as f:
            app_js_content = f.read()
        
        # Reemplazar la URL
        print(f"🔄 Reemplazando 'API_URL' por '{api_url}'...")
        updated_content = app_js_content.replace("'API_URL'", f"'{api_url}'")
        
        # Guardar cambios localmente
        print(f"💾 Guardando cambios en frontend/app.js...")
        with open("frontend/app.js", "w") as f:
            f.write(updated_content)
        
        # Subir el archivo actualizado al bucket
        print(f"📤 Subiendo app.js actualizado a {frontend_bucket}...")
        s3.put_object(
            Bucket=frontend_bucket,
            Key='app.js',
            Body=updated_content.encode('utf-8'),
            ContentType='application/javascript'
        )
        
        print("✅ Frontend URL actualizado exitosamente")
        return True
    except Exception as e:
        print(f"❌ Error actualizando frontend: {e}")
        return False

def main():
    # Configurar argumentos
    parser = argparse.ArgumentParser(
        description='Actualizar URL del API Gateway en el frontend',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Ejemplos:
  # Obtener URLs automáticamente del stack
  python3 update_frontend_url.py
  
  # Especificar URLs manualmente
  python3 update_frontend_url.py --api-url "https://api.execute-api.eu-west-1.amazonaws.com/prod/analyze" --bucket "mi-bucket"
  
  # Con región personalizada
  python3 update_frontend_url.py --region us-east-1
        '''
    )
    
    parser.add_argument('--api-url', help='URL del API Gateway (ej: https://api.execute-api.eu-west-1.amazonaws.com/prod/analyze)')
    parser.add_argument('--bucket', help='Nombre del bucket S3')
    parser.add_argument('--region', default='eu-west-1', help='Región AWS (default: eu-west-1)')
    parser.add_argument('--lab-name', help='Nombre del laboratorio para obtener stack (default: clase7-lab1-sboludaf)')
    
    args = parser.parse_args()
    
    region = args.region
    
    # Si se proporcionan URLs manualmente, usarlas directamente
    if args.api_url and args.bucket:
        api_url = args.api_url
        s3_bucket = args.bucket
        print(f"🚀 Actualizando frontend con parámetros personalizados")
        print(f"📍 Región: {region}\n")
    else:
        # Obtener del stack de CloudFormation
        lab_name = args.lab_name or os.getenv('LAB_NAME', 'clase7-lab1-sboludaf')
        stack_name = f"{lab_name}-stack"
        
        print(f"🚀 Actualizando frontend para stack: {stack_name}")
        print(f"📍 Región: {region}\n")
        
        # Obtener outputs del stack
        outputs = get_stack_outputs(stack_name, region)
        if not outputs:
            sys.exit(1)
        
        # Extraer URLs
        api_url = outputs.get('APIGatewayURL')
        s3_bucket = outputs.get('S3BucketName')
        
        if not api_url or not s3_bucket:
            print("❌ No se encontraron los outputs necesarios (APIGatewayURL, S3BucketName)")
            sys.exit(1)
    
    print(f"✓ API Gateway URL: {api_url}")
    print(f"✓ S3 Bucket: {s3_bucket}\n")
    
    # Actualizar frontend
    if update_frontend_url(api_url, s3_bucket, region):
        print(f"\n✨ Frontend actualizado correctamente")
        print(f"🌐 Accede a: http://{s3_bucket}.s3-website-{region}.amazonaws.com")
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()
