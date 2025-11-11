#!/usr/bin/env python3
"""
RAG Lab - AWS CDK Application
Despliegue completo de una aplicación RAG con Kendra, Lambda, API Gateway y Bedrock
"""

import aws_cdk as cdk
import sys
import argparse
from aws_cdk import aws_s3 as s3
from stacks.storage_stack import StorageStack
from stacks.kendra_stack import KendraStack
from stacks.lambda_stack import LambdaStack
from stacks.api_stack import ApiStack
from stacks.frontend_stack import FrontendStack


class RagLabApp(cdk.App):
    """Aplicación CDK para RAG Lab"""
    
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
        elif self.specific_stack == "kendra":
            # Para Kendra necesitamos el storage primero
            storage_stack = StorageStack(
                self,
                f"{lab_name}-storage",
                lab_name=lab_name,
                env=cdk.Environment(region=region)
            )
            kendra_stack = KendraStack(
                self,
                f"{lab_name}-kendra",
                lab_name=lab_name,
                documents_bucket=storage_stack.documents_bucket,
                kendra_role=storage_stack.kendra_role,
                env=cdk.Environment(region=region)
            )
            kendra_stack.add_dependency(storage_stack)
        elif self.specific_stack == "lambdas":
            # Para lambdas necesitamos storage y kendra
            storage_stack = StorageStack(
                self,
                f"{lab_name}-storage",
                lab_name=lab_name,
                env=cdk.Environment(region=region)
            )
            kendra_stack = KendraStack(
                self,
                f"{lab_name}-kendra",
                lab_name=lab_name,
                documents_bucket=storage_stack.documents_bucket,
                kendra_role=storage_stack.kendra_role,
                env=cdk.Environment(region=region)
            )
            kendra_stack.add_dependency(storage_stack)
            lambda_stack = LambdaStack(
                self,
                f"{lab_name}-lambdas",
                lab_name=lab_name,
                documents_bucket=storage_stack.documents_bucket,
                documents_table=storage_stack.documents_table,
                queries_table=storage_stack.queries_table,
                kendra_index_id=kendra_stack.kendra_index_id,
                kendra_index_arn=kendra_stack.kendra_index_arn,
                env=cdk.Environment(region=region)
            )
            lambda_stack.add_dependency(storage_stack)
            lambda_stack.add_dependency(kendra_stack)
        elif self.specific_stack == "api":
            # Para API necesitamos todos los anteriores
            self._deploy_all_stacks(lab_name, region, upload_frontend)
        elif self.specific_stack == "frontend":
            # Para frontend solo necesitamos recuperar el API endpoint
            self._deploy_frontend_only(lab_name, region)
    
    def _deploy_frontend_only(self, lab_name: str, region: str):
        """Desplegar solo el frontend sin recrear los stacks anteriores"""
        import boto3
        
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
            
            # Desplegar solo el frontend stack (crea su propio bucket)
            FrontendStack(
                self,
                f"{lab_name}-frontend",
                lab_name=lab_name,
                api_endpoint=api_endpoint,
                env=cdk.Environment(region=region)
            )
        except Exception as e:
            print(f"Error al recuperar el API endpoint: {e}")
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
        
        # ==================== KENDRA STACK ====================
        kendra_stack = KendraStack(
            self,
            f"{lab_name}-kendra",
            lab_name=lab_name,
            documents_bucket=storage_stack.documents_bucket,
            kendra_role=storage_stack.kendra_role,
            env=cdk.Environment(region=region)
        )
        kendra_stack.add_dependency(storage_stack)
        
        # ==================== LAMBDA STACK ====================
        lambda_stack = LambdaStack(
            self,
            f"{lab_name}-lambdas",
            lab_name=lab_name,
            documents_bucket=storage_stack.documents_bucket,
            documents_table=storage_stack.documents_table,
            queries_table=storage_stack.queries_table,
            kendra_index_id=kendra_stack.kendra_index_id,
            kendra_index_arn=kendra_stack.kendra_index_arn,
            env=cdk.Environment(region=region)
        )
        lambda_stack.add_dependency(storage_stack)
        lambda_stack.add_dependency(kendra_stack)
        
        # ==================== API STACK ====================
        api_stack = ApiStack(
            self,
            f"{lab_name}-api",
            lab_name=lab_name,
            upload_function=lambda_stack.upload_function,
            query_function=lambda_stack.query_function,
            env=cdk.Environment(region=region)
        )
        api_stack.add_dependency(lambda_stack)
        
        # ==================== FRONTEND STACK ====================
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
    parser = argparse.ArgumentParser(description="RAG Lab CDK Deployment")
    parser.add_argument("--lab-name", default="rag-lab", help="Nombre único del laboratorio")
    parser.add_argument("--region", default="eu-west-1", help="Región AWS")
    parser.add_argument("--upload-frontend", action="store_true", help="Subir frontend a S3")
    parser.add_argument("--stack", default=None, help="Stack específico a desplegar (storage, kendra, lambdas, api, frontend)")
    
    args = parser.parse_args()
    
    # Si no se especifica un stack específico (--all), activar upload_frontend por defecto
    upload_frontend = args.upload_frontend or args.stack is None
    
    app = RagLabApp(
        lab_name=args.lab_name,
        region=args.region,
        upload_frontend=upload_frontend,
        specific_stack=args.stack
    )
    
    app.synth()


if __name__ == "__main__":
    main()
