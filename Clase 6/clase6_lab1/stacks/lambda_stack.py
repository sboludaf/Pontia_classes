"""
Lambda Stack - Lambda Functions
Crea las funciones Lambda para upload y query
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_lambda as lambda_,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    Duration,
)
from constructs import Construct
import os


class LambdaStack(cdk.Stack):
    """Stack para Lambda Functions"""
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lab_name: str,
        documents_bucket: s3.Bucket,
        documents_table: dynamodb.Table,
        queries_table: dynamodb.Table,
        kendra_index_id: str,
        kendra_index_arn: str,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.lab_name = lab_name
        
        # ==================== IAM ROLE PARA LAMBDAS ====================
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            role_name=f"{lab_name}-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )
        
        # Permisos S3
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:GetObject", "s3:PutObject", "s3:ListBucket"],
                resources=[
                    documents_bucket.bucket_arn,
                    documents_bucket.arn_for_objects("*"),
                ],
            )
        )
        
        # Permisos DynamoDB
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                ],
                resources=[
                    documents_table.table_arn,
                    queries_table.table_arn,
                ],
            )
        )
        
        # Permisos Kendra
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=[
                    "kendra:Query",
                    "kendra:BatchPutDocument",
                    "kendra:StartDataSourceSyncJob",
                ],
                resources=[kendra_index_arn],
            )
        )
        
        # Permisos Bedrock
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["bedrock:*"],
                resources=["*"],
            )
        )
        
        # ==================== LAMBDA: UPLOAD HANDLER ====================
        self.upload_function = lambda_.Function(
            self,
            "UploadFunction",
            function_name=f"{lab_name}-upload",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            role=lambda_role,
            timeout=Duration.seconds(60),
            memory_size=512,
            environment={
                "DOCUMENTS_BUCKET": documents_bucket.bucket_name,
                "DOCUMENTS_TABLE": documents_table.table_name,
                "KENDRA_INDEX_ID": kendra_index_id,
            },
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../lambdas"),
                exclude=["*.pyc", "__pycache__"],
            ),
        )
        
        # ==================== LAMBDA: QUERY HANDLER ====================
        self.query_function = lambda_.Function(
            self,
            "QueryFunction",
            function_name=f"{lab_name}-query",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="index.lambda_handler",
            role=lambda_role,
            timeout=Duration.seconds(60),
            memory_size=512,
            environment={
                "DOCUMENTS_TABLE": documents_table.table_name,
                "QUERIES_TABLE": queries_table.table_name,
                "KENDRA_INDEX_ID": kendra_index_id,
            },
            code=lambda_.Code.from_asset(
                os.path.join(os.path.dirname(__file__), "../lambdas"),
                exclude=["*.pyc", "__pycache__"],
            ),
        )
        
        # ==================== OUTPUTS ====================
        cdk.CfnOutput(
            self,
            "UploadFunctionArn",
            value=self.upload_function.function_arn,
            export_name=f"{lab_name}-upload-function-arn",
        )
        
        cdk.CfnOutput(
            self,
            "QueryFunctionArn",
            value=self.query_function.function_arn,
            export_name=f"{lab_name}-query-function-arn",
        )
