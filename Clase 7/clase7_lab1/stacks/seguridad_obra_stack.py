"""
Seguridad Obra Lab - CDK Stack
Despliega toda la infraestructura del laboratorio de seguridad con AWS Rekognition
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_s3_deployment as s3deploy,
    RemovalPolicy,
    Duration,
    CfnOutput,
    StackProps
)
from constructs import Construct
import os


class SeguridadObraStack(cdk.Stack):
    """Stack completo para el laboratorio de seguridad con AWS Rekognition"""

    def __init__(self, scope: Construct, construct_id: str, lab_name: str, region: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # ==================== CONFIGURACIÓN ====================
        self.project_name = lab_name
        self.aws_region = region

        # ==================== S3 BUCKET ====================
        self.create_s3_bucket()

        # ==================== DYNAMODB TABLE ====================
        self.create_dynamodb_table()

        # ==================== LAMBDA FUNCTION ====================
        self.create_lambda_function()

        # ==================== API GATEWAY ====================
        self.create_api_gateway()

        # ==================== FRONTEND DEPLOYMENT ====================
        self.deploy_frontend()

        # ==================== OUTPUTS ====================
        self.create_outputs()

    def create_s3_bucket(self):
        """Crear bucket S3 para almacenar imágenes y frontend"""
        self.s3_bucket = s3.Bucket(
            self,
            f"{self.project_name}-Bucket",
            bucket_name=f"{self.project_name}-{self.account}-{self.region}",
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            website_index_document="index.html",
            website_error_document="error.html",
            public_read_access=True,  # Habilitar acceso público de lectura
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False
            ),
            cors=[
                s3.CorsRule(
                    allowed_origins=["*"],
                    allowed_methods=[s3.HttpMethods.GET, s3.HttpMethods.POST],
                    allowed_headers=["*"]
                )
            ]
        )

    def create_dynamodb_table(self):
        """Crear tabla DynamoDB para almacenar resultados"""
        self.dynamodb_table = dynamodb.Table(
            self,
            f"{self.project_name}-Table",
            table_name=f"{self.project_name}-analisis",
            partition_key=dynamodb.Attribute(
                name="imageId",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True
        )

    def create_lambda_function(self):
        """Crear función Lambda para procesar imágenes con Rekognition"""
        # Crear rol IAM para Lambda
        self.lambda_role = iam.Role(
            self,
            f"{self.project_name}-LambdaRole",
            role_name=f"{self.project_name}-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonRekognitionFullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3FullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonDynamoDBFullAccess"
                )
            ]
        )

        # Crear función Lambda
        self.lambda_function = lambda_.Function(
            self,
            f"{self.project_name}-Analyzer",
            function_name=f"{self.project_name}-analyzer",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            role=self.lambda_role,
            code=lambda_.Code.from_asset("lambdas"),
            timeout=Duration.seconds(30),
            memory_size=256,
            environment={
                "S3_BUCKET": self.s3_bucket.bucket_name,
                "DYNAMODB_TABLE": self.dynamodb_table.table_name
            },
            dead_letter_queue_enabled=False,
            retry_attempts=0
        )

    def create_api_gateway(self):
        """Crear API Gateway con CORS configurado"""
        self.api = apigateway.RestApi(
            self,
            f"{self.project_name}-Api",
            rest_api_name=f"{self.project_name}-api",
            description=f"API para análisis de seguridad con AWS Rekognition - {self.project_name}",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=["*"],
                allow_methods=["GET", "POST", "OPTIONS"],
                allow_headers=[
                    "Content-Type",
                    "Authorization",
                    "X-Amz-Date",
                    "X-Amz-Security-Token"
                ],
                max_age=Duration.seconds(300),
            ),
            deploy_options=apigateway.StageOptions(
                stage_name="prod",
                throttling_rate_limit=100,
                throttling_burst_limit=50
            )
        )

        # Crear recurso /analyze
        analyze_resource = self.api.root.add_resource("analyze")

        # Configurar integración con Lambda (proxy=True para que Lambda maneje la respuesta)
        lambda_integration = apigateway.LambdaIntegration(
            self.lambda_function,
            proxy=True
        )

        # Configurar método POST
        analyze_resource.add_method(
            "POST",
            lambda_integration
        )

    def deploy_frontend(self):
        """Desplegar frontend en S3"""
        s3deploy.BucketDeployment(
            self,
            f"{self.project_name}-FrontendDeployment",
            sources=[s3deploy.Source.asset("frontend")],
            destination_bucket=self.s3_bucket,
            destination_key_prefix="",
            retain_on_delete=False,
            prune=True
        )

    def create_outputs(self):
        """Crear outputs del stack"""
        CfnOutput(
            self,
            "FrontendURL",
            description="URL del frontend",
            value=f"http://{self.s3_bucket.bucket_name}.s3-website-{self.aws_region}.amazonaws.com"
        )

        CfnOutput(
            self,
            "APIGatewayURL",
            description="URL del API Gateway",
            value=f"{self.api.url}analyze"
        )

        CfnOutput(
            self,
            "LambdaFunctionName",
            description="Nombre de la función Lambda",
            value=self.lambda_function.function_name
        )

        CfnOutput(
            self,
            "DynamoDBTableName",
            description="Nombre de la tabla DynamoDB",
            value=self.dynamodb_table.table_name
        )

        CfnOutput(
            self,
            "S3BucketName",
            description="Nombre del bucket S3",
            value=self.s3_bucket.bucket_name
        )
