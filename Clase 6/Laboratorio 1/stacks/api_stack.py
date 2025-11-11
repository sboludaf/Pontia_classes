"""
API Stack - API Gateway
Crea el API Gateway REST con endpoints para upload y query
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as lambda_,
)
from constructs import Construct


class ApiStack(cdk.Stack):
    """Stack para API Gateway"""
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lab_name: str,
        upload_function: lambda_.Function,
        query_function: lambda_.Function,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.lab_name = lab_name
        
        # ==================== API GATEWAY ====================
        self.api = apigateway.RestApi(
            self,
            "RagApi",
            rest_api_name=f"{lab_name}-api",
            description="RAG API con Kendra y Bedrock",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization", "X-Amz-Date", "X-Amz-Security-Token"],
                max_age=cdk.Duration.seconds(300),
            ),
        )
        
        self.api_endpoint = self.api.url
        
        # ==================== RESOURCE: /upload ====================
        upload_resource = self.api.root.add_resource("upload")
        upload_integration = apigateway.LambdaIntegration(
            upload_function,
            proxy=True,
        )
        upload_resource.add_method("POST", upload_integration)
        
        # ==================== RESOURCE: /query ====================
        query_resource = self.api.root.add_resource("query")
        query_integration = apigateway.LambdaIntegration(
            query_function,
            proxy=True,
        )
        query_resource.add_method("POST", query_integration)
        
        # ==================== RESOURCE: /documents ====================
        documents_resource = self.api.root.add_resource("documents")
        documents_integration = apigateway.LambdaIntegration(
            upload_function,
            proxy=True,
        )
        documents_resource.add_method("GET", documents_integration)
        
        # ==================== OUTPUTS ====================
        cdk.CfnOutput(
            self,
            "ApiEndpoint",
            value=self.api_endpoint,
            export_name=f"{lab_name}-api-endpoint",
        )
        
        cdk.CfnOutput(
            self,
            "UploadEndpoint",
            value=f"{self.api_endpoint}upload",
            export_name=f"{lab_name}-upload-endpoint",
        )
        
        cdk.CfnOutput(
            self,
            "QueryEndpoint",
            value=f"{self.api_endpoint}query",
            export_name=f"{lab_name}-query-endpoint",
        )
