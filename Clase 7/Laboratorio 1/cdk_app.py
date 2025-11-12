#!/usr/bin/env python3
"""
SafetyVision Pro - AWS CDK Application
Despliegue completo de una aplicación de Computer Vision con Rekognition, Lambda, API Gateway y S3
"""

import aws_cdk as cdk
import sys
import argparse
import boto3
from aws_cdk import aws_s3 as s3
from stacks.storage_stack import StorageStack
from stacks.rekognition_stack import RekognitionStack
from stacks.lambda_stack import LambdaStack
from stacks.api_stack import ApiStack
from stacks.frontend_stack import FrontendStack


class SafetyVisionApp(cdk.App):
    """Aplicación CDK para SafetyVision Pro"""
    
    def __init__(self, lab_name: str, region: str, upload_frontend: bool, specific_stack: str = None):
        super().__init__()
        
        self.lab_name = lab_name
        self.aws_region = region
        self.upload_frontend = upload_frontend
        self.specific_stack = specific_stack
        
        # Si se especifica un stack, solo desplegar ese
        if specific_stack:
            self._deploy_specific_stack(lab_name, region, upload_frontend)
        else:
            self._deploy_all_stacks(lab_name, region, upload_frontend)
    
    def _deploy_specific_stack(self, lab_name: str, region: str, upload_frontend: bool):
        """Desplegar solo un stack específico"""
        if self.specific_stack == "storage":
            StorageStack(
                self,
                f"{lab_name}-storage",
                lab_name=lab_name,
                env=cdk.Environment(region=region)
            )
        elif self.specific_stack == "rekognition":
            # Para Rekognition necesitamos el storage primero
            storage_stack = StorageStack(
                self,
                f"{lab_name}-storage",
                lab_name=lab_name,
                env=cdk.Environment(region=region)
            )
            rekognition_stack = RekognitionStack(
                self,
                f"{lab_name}-rekognition",
                lab_name=lab_name,
                env=cdk.Environment(region=region)
            )
            rekognition_stack.add_dependency(storage_stack)
        elif self.specific_stack == "lambdas":
            # Para lambdas necesitamos storage y rekognition
            storage_stack = StorageStack(
                self,
                f"{lab_name}-storage",
                lab_name=lab_name,
                env=cdk.Environment(region=region)
            )
            rekognition_stack = RekognitionStack(
                self,
                f"{lab_name}-rekognition",
                lab_name=lab_name,
                env=cdk.Environment(region=region)
            )
            rekognition_stack.add_dependency(storage_stack)
            lambda_stack = LambdaStack(
                self,
                f"{lab_name}-lambdas",
                lab_name=lab_name,
                env=cdk.Environment(region=region)
            )
            lambda_stack.add_dependency(storage_stack)
            lambda_stack.add_dependency(rekognition_stack)
        elif self.specific_stack == "api":
            # Para API necesitamos todos los anteriores
            self._deploy_api_stack(lab_name, region)
        elif self.specific_stack == "frontend":
            # Para frontend solo necesitamos recuperar el API endpoint
            self._deploy_frontend_only(lab_name, region)
    
    def _deploy_api_stack(self, lab_name: str, region: str):
        """Desplegar solo el API stack con sus dependencias"""
        storage_stack = StorageStack(
            self,
            f"{lab_name}-storage",
            lab_name=lab_name,
            env=cdk.Environment(region=region)
        )
        
        rekognition_stack = RekognitionStack(
            self,
            f"{lab_name}-rekognition",
            lab_name=lab_name,
            env=cdk.Environment(region=region)
        )
        rekognition_stack.add_dependency(storage_stack)
        
        lambda_stack = LambdaStack(
            self,
            f"{lab_name}-lambdas",
            lab_name=lab_name,
            env=cdk.Environment(region=region)
        )
        lambda_stack.add_dependency(storage_stack)
        lambda_stack.add_dependency(rekognition_stack)
        
        api_stack = ApiStack(
            self,
            f"{lab_name}-api",
            lab_name=lab_name,
            upload_function=lambda_stack.upload_function,
            analysis_function=lambda_stack.analysis_function,
            dashboard_function=lambda_stack.dashboard_function,
            report_function=lambda_stack.report_function,
            env=cdk.Environment(region=region)
        )
        api_stack.add_dependency(lambda_stack)
    
    def _deploy_frontend_only(self, lab_name: str, region: str):
        """Desplegar solo el frontend sin recrear los stacks anteriores"""
        # Recuperar el API endpoint del stack existente
        cf_client = boto3.client('cloudformation', region_name=region)
        
        try:
            # Obtener el API stack para el endpoint
            api_stack_name = f"{lab_name}-api"
            api_response = cf_client.describe_stacks(StackName=api_stack_name)
            api_outputs = {o['OutputKey']: o['OutputValue'] for o in api_response['Stacks'][0].get('Outputs', [])}
            
            api_endpoint = api_outputs.get('ApiEndpoint')
            
            if not api_endpoint:
                raise Exception(f"No se encontró el API endpoint. API outputs: {api_outputs}")
            
            print(f"✅ API endpoint recuperado: {api_endpoint}")
            
            # Desplegar solo el frontend stack (crea su propio bucket)
            FrontendStack(
                self,
                f"{lab_name}-frontend",
                lab_name=lab_name,
                api_endpoint=api_endpoint,
                env=cdk.Environment(region=region)
            )
        except Exception as e:
            print(f"❌ Error al recuperar el API endpoint: {e}")
            print("Asegúrate de que ya has desplegado el stack API")
            raise
    
    def _deploy_all_stacks(self, lab_name: str, region: str, upload_frontend: bool):
        """Desplegar todos los stacks"""
        # ==================== STORAGE STACK ====================
        storage_stack = StorageStack(
            self,
            f"{lab_name}-storage",
            lab_name=lab_name,
            env=cdk.Environment(region=region)
        )
        
        # ==================== REKOGNITION STACK ====================
        rekognition_stack = RekognitionStack(
            self,
            f"{lab_name}-rekognition",
            lab_name=lab_name,
            env=cdk.Environment(region=region)
        )
        rekognition_stack.add_dependency(storage_stack)
        
        # ==================== LAMBDA STACK ====================
        lambda_stack = LambdaStack(
            self,
            f"{lab_name}-lambdas",
            lab_name=lab_name,
            env=cdk.Environment(region=region)
        )
        lambda_stack.add_dependency(storage_stack)
        lambda_stack.add_dependency(rekognition_stack)
        
        # ==================== API STACK ====================
        api_stack = ApiStack(
            self,
            f"{lab_name}-api",
            lab_name=lab_name,
            upload_function=lambda_stack.upload_function,
            analysis_function=lambda_stack.analysis_function,
            dashboard_function=lambda_stack.dashboard_function,
            report_function=lambda_stack.report_function,
            env=cdk.Environment(region=region)
        )
        api_stack.add_dependency(lambda_stack)
        
        # ==================== FRONTEND STACK ====================
        if upload_frontend:
            frontend_stack = FrontendStack(
                self,
                f"{lab_name}-frontend",
                lab_name=lab_name,
                api_endpoint=api_stack.api_endpoint,
                env=cdk.Environment(region=region)
            )
            frontend_stack.add_dependency(api_stack)


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="SafetyVision Pro CDK Deployment")
    parser.add_argument("--lab-name", default=None, help="Nombre único del laboratorio")
    parser.add_argument("--region", default=None, help="Región AWS")
    parser.add_argument("--upload-frontend", action="store_true", help="Subir frontend a S3")
    parser.add_argument("--stack", default=None, help="Stack específico a desplegar (storage, rekognition, lambdas, api, frontend)")
    
    args = parser.parse_args()
    
    # Obtener valores desde el contexto de CDK o argumentos
    app = cdk.App()
    
    # Prioridad: argumentos de línea de comandos > contexto de CDK > valores por defecto
    lab_name = args.lab_name or app.node.try_get_context("lab_name") or "safety-vision-finn"
    region = args.region or app.node.try_get_context("region") or "eu-west-1"
    
    # Si no se especifica upload_frontend, usar el contexto
    upload_frontend = args.upload_frontend
    if upload_frontend is False:
        upload_frontend = app.node.try_get_context("upload_frontend") or False
    
    # Si no se especifica un stack específico (--all), activar upload_frontend por defecto
    if args.stack is None and upload_frontend is False:
        upload_frontend = True
    
    safety_app = SafetyVisionApp(
        lab_name=lab_name,
        region=region,
        upload_frontend=upload_frontend,
        specific_stack=args.stack
    )
    
    safety_app.synth()


if __name__ == "__main__":
    main()
