#!/usr/bin/env python3
"""
Newsletter Lab - Despliegue completo con CDK Python
Usa archivos externos para Lambdas y Frontend
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_sns as sns,
    aws_dynamodb as dynamodb,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    aws_logs as logs,
    aws_s3 as s3,
    Duration,
    RemovalPolicy,
)
from constructs import Construct
import sys
import argparse
import boto3
import time
import os
import json


class NewsletterLabCompleteStack(cdk.Stack):
    """Stack completo que incluye Backend y Frontend"""

    def __init__(self, scope: Construct, construct_id: str, lab_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        self.lab_name = lab_name

        # ==================== SNS TOPIC ====================
        newsletter_topic = sns.Topic(
            self,
            "NewsletterTopic",
            topic_name=f"{lab_name}-topic",
            display_name=f"{lab_name} Topic",
        )

        # ==================== DYNAMODB TABLE ====================
        subscribers_table = dynamodb.Table(
            self,
            "SubscribersTable",
            table_name=f"{lab_name}-subscribers",
            partition_key=dynamodb.Attribute(
                name="email", type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
        )

        # ==================== IAM ROLE ====================
        lambda_role = iam.Role(
            self,
            "LambdaExecutionRole",
            role_name=f"{lab_name}-lambda-execution-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaBasicExecutionRole"
                )
            ],
        )

        # Permisos DynamoDB
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "dynamodb:PutItem",
                    "dynamodb:GetItem",
                    "dynamodb:UpdateItem",
                    "dynamodb:Query",
                    "dynamodb:Scan",
                ],
                resources=[subscribers_table.table_arn],
            )
        )

        # Permisos SNS
        lambda_role.add_to_policy(
            iam.PolicyStatement(
                actions=["sns:Publish", "sns:Subscribe"],
                resources=[newsletter_topic.topic_arn],
            )
        )

        # ==================== LAMBDAS ====================
        register_function = lambda_.Function(
            self,
            "RegisterUserFunction",
            function_name=f"{lab_name}-register-user",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="register.lambda_handler",
            role=lambda_role,
            environment={
                "SUBSCRIBERS_TABLE": subscribers_table.table_name,
                "SNS_TOPIC_ARN": newsletter_topic.topic_arn,
            },
            code=lambda_.Code.from_asset("resources/lambdas"),
            timeout=Duration.seconds(30),
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        publish_function = lambda_.Function(
            self,
            "PublishMessageFunction",
            function_name=f"{lab_name}-publish-message",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="publish.lambda_handler",
            role=lambda_role,
            environment={
                "SUBSCRIBERS_TABLE": subscribers_table.table_name,
                "SNS_TOPIC_ARN": newsletter_topic.topic_arn,
            },
            code=lambda_.Code.from_asset("resources/lambdas"),
            timeout=Duration.seconds(30),
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        subscribers_function = lambda_.Function(
            self,
            "GetSubscribersFunction",
            function_name=f"{lab_name}-get-subscribers",
            runtime=lambda_.Runtime.PYTHON_3_11,
            handler="subscribers.lambda_handler",
            role=lambda_role,
            environment={
                "SUBSCRIBERS_TABLE": subscribers_table.table_name,
            },
            code=lambda_.Code.from_asset("resources/lambdas"),
            timeout=Duration.seconds(30),
            log_retention=logs.RetentionDays.ONE_WEEK,
        )

        # ==================== API GATEWAY ====================
        self.api = apigateway.RestApi(
            self,
            "NewsletterApi",
            rest_api_name=f"{lab_name}-api",
            description=f"{lab_name} API",
            endpoint_types=[apigateway.EndpointType.REGIONAL],
        )

        # Register resource
        register_resource = self.api.root.add_resource("register")
        register_integration = apigateway.LambdaIntegration(register_function, proxy=True)
        register_resource.add_method("POST", register_integration)
        register_resource.add_method("OPTIONS", register_integration)

        # Publish resource
        publish_resource = self.api.root.add_resource("publish")
        publish_integration = apigateway.LambdaIntegration(publish_function, proxy=True)
        publish_resource.add_method("POST", publish_integration)
        publish_resource.add_method("OPTIONS", publish_integration)

        # Subscribers resource
        subscribers_resource = self.api.root.add_resource("subscribers")
        subscribers_integration = apigateway.LambdaIntegration(
            subscribers_function, proxy=True
        )
        subscribers_resource.add_method("GET", subscribers_integration)
        subscribers_resource.add_method("OPTIONS", subscribers_integration)

        # ==================== S3 BUCKET ====================
        account_id = cdk.Stack.of(self).account
        bucket_name = f"{lab_name}-{account_id}"

        frontend_bucket = s3.Bucket(
            self,
            "FrontendBucket",
            bucket_name=bucket_name,
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
        )

        # Políticas de bucket
        frontend_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["s3:GetObject"],
                resources=[frontend_bucket.arn_for_objects("*")],
            )
        )

        frontend_bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.AnyPrincipal()],
                actions=["s3:ListBucket"],
                resources=[frontend_bucket.bucket_arn],
            )
        )

        # Configurar website
        cfn_bucket = frontend_bucket.node.default_child
        cfn_bucket.website_configuration = s3.CfnBucket.WebsiteConfigurationProperty(
            index_document="index.html",
            error_document="index.html",
        )

        # ==================== OUTPUTS ====================
        cdk.CfnOutput(
            self,
            "NewsletterTopicArn",
            value=newsletter_topic.topic_arn,
            export_name=f"{lab_name}-TopicArn",
            description="ARN del tema SNS",
        )

        cdk.CfnOutput(
            self,
            "SubscribersTableName",
            value=subscribers_table.table_name,
            export_name=f"{lab_name}-SubscribersTableName",
            description="Nombre de la tabla DynamoDB",
        )

        cdk.CfnOutput(
            self,
            "ApiEndpoint",
            value=f"https://{self.api.rest_api_id}.execute-api.{self.region}.amazonaws.com/prod",
            export_name=f"{lab_name}-ApiEndpoint",
            description="API Gateway Endpoint",
        )

        cdk.CfnOutput(
            self,
            "BucketName",
            value=frontend_bucket.bucket_name,
            export_name=f"{lab_name}-BucketName",
            description="Nombre del bucket S3",
        )

        cdk.CfnOutput(
            self,
            "WebsiteUrl",
            value=frontend_bucket.bucket_website_url,
            export_name=f"{lab_name}-WebsiteUrl",
            description="URL del website S3 Static Hosting",
        )


def upload_frontend_to_s3(lab_name: str, account_id: str, region: str, api_endpoint: str):
    """Subir el frontend a S3 con la URL del API Gateway"""
    try:
        print(f"\n📤 Subiendo frontend a S3...")

        # Esperar a que el stack esté completamente disponible
        time.sleep(5)

        # Obtener nombre del bucket
        cf_client = boto3.client("cloudformation", region_name=region)
        s3_client = boto3.client("s3", region_name=region)

        try:
            response = cf_client.describe_stacks(StackName=f"{lab_name}-stack")
            outputs = {
                o["OutputKey"]: o["OutputValue"] for o in response["Stacks"][0]["Outputs"]
            }
            bucket_name = outputs.get("BucketName")

            if not bucket_name:
                print("⚠️  No se encontró el nombre del bucket en los outputs")
                return False

            # Subir archivos del frontend
            frontend_dir = "resources/frontend"

            # Crear config.json con la URL del API Gateway
            config_json = json.dumps({"apiEndpoint": api_endpoint})
            s3_client.put_object(
                Bucket=bucket_name,
                Key="config.json",
                Body=config_json.encode("utf-8"),
                ContentType="application/json",
                CacheControl="max-age=0",
            )
            print("✅ config.json subido")

            # Subir archivos estáticos
            files_to_upload = ["index.html", "styles.css", "app.js", "config.js"]
            for filename in files_to_upload:
                filepath = os.path.join(frontend_dir, filename)
                if os.path.exists(filepath):
                    with open(filepath, "r") as f:
                        content = f.read()

                    content_type = (
                        "text/html"
                        if filename.endswith(".html")
                        else "text/css"
                        if filename.endswith(".css")
                        else "application/json"
                        if filename.endswith(".json")
                        else "application/javascript"
                    )

                    s3_client.put_object(
                        Bucket=bucket_name,
                        Key=filename,
                        Body=content.encode("utf-8"),
                        ContentType=content_type,
                        CacheControl="max-age=0",
                    )
                    print(f"✅ {filename} subido")

            website_url = outputs.get(
                "WebsiteUrl",
                f"http://{bucket_name}.s3-website-{region}.amazonaws.com",
            )
            print(f"\n✅ Frontend subido exitosamente")
            print(f"🌐 Acceder a: {website_url}")
            return True

        except cf_client.exceptions.ClientError as e:
            if "does not exist" in str(e):
                print(
                    "⚠️  El stack aún no está disponible. Intenta de nuevo en unos momentos."
                )
            else:
                print(f"❌ Error: {e}")
            return False

    except Exception as e:
        print(f"❌ Error al subir frontend: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Newsletter Lab - CDK Deployment")
    parser.add_argument(
        "--lab-name",
        default="newsletter-lab",
        help="Nombre único del laboratorio (default: newsletter-lab)",
    )
    parser.add_argument(
        "--account",
        default=os.getenv("AWS_ACCOUNT_ID", "838205824064"),
        help="AWS Account ID (default: from AWS_ACCOUNT_ID env var or 838205824064)",
    )
    parser.add_argument(
        "--region",
        default="eu-west-1",
        help="AWS Region (default: eu-west-1)",
    )
    parser.add_argument(
        "--upload-frontend",
        action="store_true",
        help="Subir frontend a S3 después del despliegue",
    )

    args = parser.parse_args()

    app = cdk.App()

    stack = NewsletterLabCompleteStack(
        app,
        f"{args.lab_name}-stack",
        lab_name=args.lab_name,
        env=cdk.Environment(account=args.account, region=args.region),
    )

    app.synth()

    # Si se especifica --upload-frontend, subir después de synth
    if args.upload_frontend:
        # Obtener el API endpoint del stack desde CloudFormation
        cf_client = boto3.client("cloudformation", region_name=args.region)
        try:
            response = cf_client.describe_stacks(StackName=f"{args.lab_name}-stack")
            outputs = {
                o["OutputKey"]: o["OutputValue"] for o in response["Stacks"][0]["Outputs"]
            }
            api_endpoint = outputs.get("ApiEndpoint")
            if api_endpoint:
                upload_frontend_to_s3(args.lab_name, args.account, args.region, api_endpoint)
            else:
                print("❌ No se encontró ApiEndpoint en los outputs")
        except Exception as e:
            print(f"❌ Error obteniendo API endpoint: {e}")


if __name__ == "__main__":
    main()
