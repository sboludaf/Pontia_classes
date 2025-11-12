"""
Frontend Stack - S3 Static Hosting
Sube el frontend a S3 con la URL del API inyectada
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_s3_deployment as s3_deployment,
    aws_iam as iam,
    RemovalPolicy,
)
from constructs import Construct
import os
import json


class FrontendStack(cdk.Stack):
    """Stack para Frontend"""
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lab_name: str,
        api_endpoint: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.lab_name = lab_name
        
        # ==================== S3 BUCKET PARA FRONTEND ====================
        self.frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=f"{lab_name}-frontend-{self.account}",
            versioned=True,
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            website_index_document="index.html",
            website_error_document="index.html",
        )
        
        # Política de acceso público para frontend
        self.frontend_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject"],
                resources=[self.frontend_bucket.arn_for_objects("*")],
            )
        )
        
        # ==================== CREAR CONFIG.JSON ====================
        config_content = {
            "apiEndpoint": api_endpoint,
            "labName": lab_name,
        }
        
        print(f"🔧 Creando configuración del frontend:")
        print(f"   - API Endpoint: {api_endpoint}")
        print(f"   - Lab Name: {lab_name}")
        print(f"   - Frontend Bucket: {self.frontend_bucket.bucket_name}")
        
        # Guardar config.json temporalmente
        config_path = "/tmp/config.json"
        with open(config_path, "w") as f:
            json.dump(config_content, f)
        
        print(f"✅ Config.json creado temporalmente en: {config_path}")
        
        # ==================== SUBIR FRONTEND ====================
        print(f"🚀 Iniciando despliegue del frontend...")
        print(f"   - Source: {os.path.join(os.path.dirname(__file__), '../frontend')}")
        print(f"   - Destination: {self.frontend_bucket.bucket_name}")
        
        s3_deployment.BucketDeployment(
            self,
            "DeployFrontend",
            sources=[
                s3_deployment.Source.asset(
                    os.path.join(os.path.dirname(__file__), "../frontend")
                ),
                s3_deployment.Source.json_data("config.json", config_content),
            ],
            destination_bucket=self.frontend_bucket,
            destination_key_prefix="",
            memory_limit=512,
        )
        
        print(f"✅ Frontend desplegado exitosamente!")
        print(f"🌐 URL del frontend: http://{self.frontend_bucket.bucket_name}.s3-website-eu-west-1.amazonaws.com")
        
        # ==================== OUTPUTS ====================
        cdk.CfnOutput(
            self,
            "FrontendBucketName",
            value=self.frontend_bucket.bucket_name,
            description="Nombre del bucket S3 del frontend"
        )
        
        cdk.CfnOutput(
            self,
            "FrontendUrl",
            value=self.frontend_bucket.bucket_website_url,
            description="URL del sitio web estático"
        )
        
        cdk.CfnOutput(
            self,
            "ApiEndpoint",
            value=api_endpoint,
            description="Endpoint del API Gateway"
        )
