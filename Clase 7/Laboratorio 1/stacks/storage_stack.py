from aws_cdk import (
    Stack,
    RemovalPolicy,
    CfnOutput,
    Duration,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_kms as kms,
)
from constructs import Construct

class StorageStack(Stack):
    """Storage stack with S3 buckets and DynamoDB tables"""
    
    def __init__(self, scope: Construct, construct_id: str, lab_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self._lab_name = lab_name
        
        # KMS key for encryption
        self.encryption_key = kms.Key(
            self,
            "EncryptionKey",
            enable_key_rotation=True,
            description=f"KMS key for {self._lab_name} SafetyVision Pro",
        )
        
        # S3 Buckets
        self.images_bucket = s3.Bucket(
            self,
            "ImagesBucket",
            bucket_name=f"{self._lab_name}-images",
            versioned=True,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.encryption_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            lifecycle_rules=[
                s3.LifecycleRule(
                    id="DeleteOldImages",
                    enabled=True,
                    expiration=Duration.days(90),
                    noncurrent_version_expiration=Duration.days(30),
                )
            ]
        )
        
        self.reports_bucket = s3.Bucket(
            self,
            "ReportsBucket",
            bucket_name=f"{self._lab_name}-reports",
            versioned=True,
            encryption=s3.BucketEncryption.KMS,
            encryption_key=self.encryption_key,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )
        
        # DynamoDB Tables
        self.analysis_table = dynamodb.Table(
            self,
            "AnalysisTable",
            table_name=f"{self._lab_name}-analysis",
            partition_key=dynamodb.Attribute(name="image_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="timestamp", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            stream=dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )
        
        # Add GSI for site-based queries
        self.analysis_table.add_global_secondary_index(
            index_name="SiteIndex",
            partition_key=dynamodb.Attribute(name="site_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="analyzed_at", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        
        self.stats_table = dynamodb.Table(
            self,
            "StatsTable",
            table_name=f"{self._lab_name}-stats",
            partition_key=dynamodb.Attribute(name="site_id", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="date", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
            removal_policy=RemovalPolicy.DESTROY,
            point_in_time_recovery=True,
            encryption=dynamodb.TableEncryption.AWS_MANAGED,
        )
        
        # Add GSI for date-based queries
        self.stats_table.add_global_secondary_index(
            index_name="DateIndex",
            partition_key=dynamodb.Attribute(name="date", type=dynamodb.AttributeType.STRING),
            sort_key=dynamodb.Attribute(name="site_id", type=dynamodb.AttributeType.STRING),
            projection_type=dynamodb.ProjectionType.ALL,
        )
        
        # IAM Role for Rekognition
        self.rekognition_role = iam.Role(
            self,
            "RekognitionRole",
            role_name=f"{self._lab_name}-rekognition-role",
            assumed_by=iam.ServicePrincipal("rekognition.amazonaws.com"),
            inline_policies={
                "S3Access": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:ListBucket",
                                "s3:PutObject",
                            ],
                            resources=[
                                self.images_bucket.bucket_arn,
                                self.images_bucket.arn_for_objects("*"),
                            ],
                        )
                    ]
                ),
                "KMSAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "kms:Decrypt",
                                "kms:GenerateDataKey",
                            ],
                            resources=[self.encryption_key.key_arn],
                        )
                    ]
                )
            }
        )
        
        # IAM Role for Lambda functions
        self.lambda_role = iam.Role(
            self,
            "LambdaRole",
            role_name=f"{self._lab_name}-lambda-role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaBasicExecutionRole")
            ],
            inline_policies={
                "S3Access": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "s3:GetObject",
                                "s3:PutObject",
                                "s3:DeleteObject",
                                "s3:ListBucket",
                            ],
                            resources=[
                                self.images_bucket.bucket_arn,
                                self.images_bucket.arn_for_objects("*"),
                                self.reports_bucket.bucket_arn,
                                self.reports_bucket.arn_for_objects("*"),
                            ],
                        )
                    ]
                ),
                "DynamoDBAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "dynamodb:PutItem",
                                "dynamodb:GetItem",
                                "dynamodb:UpdateItem",
                                "dynamodb:Query",
                                "dynamodb:Scan",
                                "dynamodb:BatchGetItem",
                                "dynamodb:BatchWriteItem",
                            ],
                            resources=[
                                self.analysis_table.table_arn,
                                self.stats_table.table_arn,
                                f"{self.analysis_table.table_arn}/index/*",
                                f"{self.stats_table.table_arn}/index/*",
                            ],
                        )
                    ]
                ),
                "RekognitionAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "rekognition:DetectLabels",
                                "rekognition:DetectProtectiveEquipment",
                                "rekognition:IndexFaces",
                                "rekognition:SearchFacesByImage",
                                "rekognition:CreateCollection",
                                "rekognition:DeleteCollection",
                            ],
                            resources=["*"],
                        )
                    ]
                ),
                "KMSAccess": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "kms:Decrypt",
                                "kms:GenerateDataKey",
                                "kms:Encrypt",
                            ],
                            resources=[self.encryption_key.key_arn],
                        )
                    ]
                )
            }
        )
        
        # Outputs
        CfnOutput(self, "ImagesBucketName", value=self.images_bucket.bucket_name)
        CfnOutput(self, "ReportsBucketName", value=self.reports_bucket.bucket_name)
        CfnOutput(self, "AnalysisTableName", value=self.analysis_table.table_name)
        CfnOutput(self, "StatsTableName", value=self.stats_table.table_name)
        CfnOutput(self, "RekognitionRoleArn", value=self.rekognition_role.role_arn)
        CfnOutput(self, "LambdaRoleArn", value=self.lambda_role.role_arn)
        CfnOutput(self, "KmsKeyId", value=self.encryption_key.key_id)
