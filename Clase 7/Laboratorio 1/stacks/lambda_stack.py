from aws_cdk import (
    Stack,
    Duration,
    RemovalPolicy,
    CfnOutput,
    aws_s3 as s3,
    aws_dynamodb as dynamodb,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_lambda_event_sources as lambda_events,
    aws_sns as sns,
)
from constructs import Construct

class LambdaStack(Stack):
    """Lambda functions stack for image processing and analysis"""
    
    def __init__(self, scope: Construct, construct_id: str, lab_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self._lab_name = lab_name
        
        # Get references to storage stack resources
        self.images_bucket = s3.Bucket.from_bucket_name(
            self, "ImagesBucket", f"{self._lab_name}-images"
        )
        self.reports_bucket = s3.Bucket.from_bucket_name(
            self, "ReportsBucket", f"{self._lab_name}-reports"
        )
        self.analysis_table = dynamodb.Table.from_table_name(
            self, "AnalysisTable", f"{self._lab_name}-analysis"
        )
        self.stats_table = dynamodb.Table.from_table_name(
            self, "StatsTable", f"{self._lab_name}-stats"
        )
        
        # Import Lambda execution role from storage stack
        self.lambda_role = iam.Role.from_role_arn(
            self,
            "LambdaRole",
            f"arn:aws:iam::838205824064:role/{self._lab_name}-lambda-role"
        )
        
        # Lambda Functions
        
        # 1. Upload Function - Handles image uploads
        self.upload_function = _lambda.Function(
            self,
            "UploadFunction",
            function_name=f"{self._lab_name}-upload",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="upload_handler.lambda_handler",
            role=self.lambda_role,
            code=_lambda.Code.from_asset("lambdas"),
            timeout=Duration.minutes(5),
            memory_size=512,
                        environment={
                "IMAGES_BUCKET": self.images_bucket.bucket_name,
                "ANALYSIS_TABLE": self.analysis_table.table_name,
                "STATS_TABLE": self.stats_table.table_name,
                "REGION": "eu-west-1",
                "LAB_NAME": self._lab_name,
            },
            dead_letter_queue_enabled=True,
            retry_attempts=2,
        )
        
        # 2. Analysis Function - Processes images with Rekognition
        self.analysis_function = _lambda.Function(
            self,
            "AnalysisFunction",
            function_name=f"{self._lab_name}-analyze",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="analysis_handler.lambda_handler",
            role=self.lambda_role,
            code=_lambda.Code.from_asset("lambdas"),
            timeout=Duration.minutes(10),
            memory_size=1024,
                        environment={
                "IMAGES_BUCKET": self.images_bucket.bucket_name,
                "ANALYSIS_TABLE": self.analysis_table.table_name,
                "STATS_TABLE": self.stats_table.table_name,
                "REGION": "eu-west-1",
                "LAB_NAME": self._lab_name,
                "SNS_TOPIC_ARN": f"arn:aws:sns:eu-west-1:${{AWS::AccountId}}:{self._lab_name}-safety-alerts",
            },
            dead_letter_queue_enabled=True,
            retry_attempts=1,
        )
        
        # 3. Dashboard Function - Provides dashboard data and reports
        self.dashboard_function = _lambda.Function(
            self,
            "DashboardFunction",
            function_name=f"{self._lab_name}-dashboard",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="dashboard_handler.lambda_handler",
            role=self.lambda_role,
            code=_lambda.Code.from_asset("lambdas"),
            timeout=Duration.minutes(5),
            memory_size=256,
                        environment={
                "ANALYSIS_TABLE": self.analysis_table.table_name,
                "STATS_TABLE": self.stats_table.table_name,
                "REGION": "eu-west-1",
                "LAB_NAME": self._lab_name,
            },
            dead_letter_queue_enabled=True,
            retry_attempts=2,
        )
        
        # 4. Report Generator Function - Generates PDF reports
        self.report_function = _lambda.Function(
            self,
            "ReportFunction",
            function_name=f"{self._lab_name}-report-generator",
            runtime=_lambda.Runtime.PYTHON_3_11,
            handler="report_handler.lambda_handler",
            role=self.lambda_role,
            code=_lambda.Code.from_asset("lambdas"),
            timeout=Duration.minutes(15),
            memory_size=512,
                        environment={
                "ANALYSIS_TABLE": self.analysis_table.table_name,
                "STATS_TABLE": self.stats_table.table_name,
                "REPORTS_BUCKET": self.reports_bucket.bucket_name,
                "REGION": "eu-west-1",
                "LAB_NAME": self._lab_name,
            },
            layers=[
                # Add layers for PDF generation and image processing if needed
            ],
        )
        
        # Grant permissions to Lambda functions
        
        # Upload function permissions
        self.images_bucket.grant_put(self.upload_function)
        self.images_bucket.grant_read(self.upload_function)
        self.analysis_table.grant_write_data(self.upload_function)
        self.stats_table.grant_write_data(self.upload_function)
        
        # Analysis function permissions
        self.images_bucket.grant_read(self.analysis_function)
        self.analysis_table.grant_read_write_data(self.analysis_function)
        self.stats_table.grant_write_data(self.analysis_function)
        
        # Dashboard function permissions
        self.analysis_table.grant_read_data(self.dashboard_function)
        self.stats_table.grant_read_data(self.dashboard_function)
        
        # Report function permissions
        self.analysis_table.grant_read_data(self.report_function)
        self.stats_table.grant_read_data(self.report_function)
        self.reports_bucket.grant_put(self.report_function)
        
        # Create event source mappings for async processing
        # Note: Event sources will be configured manually after deployment
        # due to cross-stack reference limitations
        
        # CloudWatch Alarms for Lambda functions
        from aws_cdk import aws_cloudwatch as cloudwatch
        
        # Error rate alarm for upload function
        self.upload_error_alarm = cloudwatch.Alarm(
            self,
            "UploadFunctionErrorAlarm",
            metric=self.upload_function.metric_errors(),
            threshold=5,
            evaluation_periods=2,
            alarm_description="Upload function error rate is too high",
        )
        
        # Error rate alarm for analysis function
        self.analysis_error_alarm = cloudwatch.Alarm(
            self,
            "AnalysisFunctionErrorAlarm",
            metric=self.analysis_function.metric_errors(),
            threshold=5,
            evaluation_periods=2,
            alarm_description="Analysis function error rate is too high",
        )
        
        # Duration alarm for analysis function
        self.analysis_duration_alarm = cloudwatch.Alarm(
            self,
            "AnalysisFunctionDurationAlarm",
            metric=self.analysis_function.metric_duration(),
            threshold=Duration.minutes(8).to_seconds(),
            evaluation_periods=2,
            alarm_description="Analysis function duration is too high",
        )
        
        # Outputs
        CfnOutput(self, "UploadFunctionArn", value=self.upload_function.function_arn)
        CfnOutput(self, "UploadFunctionName", value=self.upload_function.function_name)
        CfnOutput(self, "AnalysisFunctionArn", value=self.analysis_function.function_arn)
        CfnOutput(self, "AnalysisFunctionName", value=self.analysis_function.function_name)
        CfnOutput(self, "DashboardFunctionArn", value=self.dashboard_function.function_arn)
        CfnOutput(self, "DashboardFunctionName", value=self.dashboard_function.function_name)
        CfnOutput(self, "ReportFunctionArn", value=self.report_function.function_arn)
        CfnOutput(self, "ReportFunctionName", value=self.report_function.function_name)
        
        # Store Lambda ARNs in Parameter Store for easy access
        from aws_cdk import aws_ssm as ssm
        
        ssm.StringParameter(
            self,
            "UploadFunctionArnParameter",
            parameter_name=f"/safety-vision/{self._lab_name}/upload-function-arn",
            string_value=self.upload_function.function_arn,
            description="Upload Lambda Function ARN",
        )
        
        ssm.StringParameter(
            self,
            "AnalysisFunctionArnParameter",
            parameter_name=f"/safety-vision/{self._lab_name}/analysis-function-arn",
            string_value=self.analysis_function.function_arn,
            description="Analysis Lambda Function ARN",
        )
        
        ssm.StringParameter(
            self,
            "DashboardFunctionArnParameter",
            parameter_name=f"/safety-vision/{self._lab_name}/dashboard-function-arn",
            string_value=self.dashboard_function.function_arn,
            description="Dashboard Lambda Function ARN",
        )
