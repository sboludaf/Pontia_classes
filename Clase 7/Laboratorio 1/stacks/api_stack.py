"""
API Stack - API Gateway
Crea el API Gateway REST con endpoints para SafetyVision Pro
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_apigateway as apigateway,
    aws_lambda as _lambda,
)
from constructs import Construct


class ApiStack(cdk.Stack):
    """Stack para API Gateway"""
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lab_name: str,
        upload_function: _lambda.Function,
        analysis_function: _lambda.Function,
        dashboard_function: _lambda.Function,
        report_function: _lambda.Function,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self._lab_name = lab_name
        
        # ==================== API GATEWAY ====================
        self.api = apigateway.RestApi(
            self,
            "SafetyVisionAPI",
            rest_api_name=f"{lab_name}-api",
            description="SafetyVision Pro - Computer Vision API for Construction Safety",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                allow_headers=["Content-Type", "Authorization", "X-Amz-Date", "X-Amz-Security-Token", "X-Requested-With"],
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
        
        # ==================== RESOURCE: /analyze ====================
        analyze_resource = self.api.root.add_resource("analyze")
        analyze_integration = apigateway.LambdaIntegration(
            analysis_function,
            proxy=True,
        )
        analyze_resource.add_method("POST", analyze_integration)
        
        # ==================== RESOURCE: /dashboard ====================
        dashboard_resource = self.api.root.add_resource("dashboard")
        dashboard_integration = apigateway.LambdaIntegration(
            dashboard_function,
            proxy=True,
        )
        dashboard_resource.add_method("GET", dashboard_integration)
        
        # ==================== RESOURCE: /stats ====================
        stats_resource = self.api.root.add_resource("stats")
        stats_integration = apigateway.LambdaIntegration(
            dashboard_function,
            proxy=True,
        )
        stats_resource.add_method("GET", stats_integration)
        
        # ==================== RESOURCE: /reports ====================
        reports_resource = self.api.root.add_resource("reports")
        reports_integration = apigateway.LambdaIntegration(
            report_function,
            proxy=True,
        )
        reports_resource.add_method("GET", reports_integration)
        
        # ==================== RESOURCE: /documents ====================
        documents_resource = self.api.root.add_resource("documents")
        documents_integration = apigateway.LambdaIntegration(
            dashboard_function,
            proxy=True,
        )
        documents_resource.add_method("GET", documents_integration)
        
        # ==================== RESOURCE: /health ====================
        health_resource = self.api.root.add_resource("health")
        health_integration = apigateway.MockIntegration(
            integration_responses=[{
                "statusCode": "200",
                "responseTemplates": {
                    "application/json": '{"status": "healthy", "service": "SafetyVision Pro API"}'
                }
            }],
            passthrough_behavior=apigateway.PassthroughBehavior.NEVER,
            request_templates={
                "application/json": '{"statusCode": 200}'
            }
        )
        health_resource.add_method("GET", health_integration)
        
        # ==================== OUTPUTS ====================
        cdk.CfnOutput(
            self,
            "ApiEndpoint",
            value=self.api_endpoint,
        )
        
        cdk.CfnOutput(
            self,
            "UploadEndpoint",
            value=f"{self.api_endpoint}upload",
        )
        
        cdk.CfnOutput(
            self,
            "AnalysisEndpoint",
            value=f"{self.api_endpoint}analyze",
        )
        
        cdk.CfnOutput(
            self,
            "DashboardEndpoint",
            value=f"{self.api_endpoint}dashboard",
        )
        
        cdk.CfnOutput(
            self,
            "StatsEndpoint",
            value=f"{self.api_endpoint}stats",
        )
        
        cdk.CfnOutput(
            self,
            "ReportsEndpoint",
            value=f"{self.api_endpoint}reports",
        )
        
        cdk.CfnOutput(
            self,
            "DocumentsEndpoint",
            value=f"{self.api_endpoint}documents",
        )
        
        cdk.CfnOutput(
            self,
            "HealthEndpoint",
            value=f"{self.api_endpoint}health",
        )
