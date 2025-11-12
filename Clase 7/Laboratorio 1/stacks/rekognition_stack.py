from aws_cdk import (
    Stack,
    CfnOutput,
    aws_rekognition as rekognition,
    aws_sns as sns,
    aws_iam as iam,
)
from constructs import Construct

class RekognitionStack(Stack):
    """Rekognition stack with collections and custom labels"""
    
    def __init__(self, scope: Construct, construct_id: str, lab_name: str, **kwargs):
        super().__init__(scope, construct_id, **kwargs)
        
        self._lab_name = lab_name
        
        # Rekognition Collection for PPE detection
        self.ppe_collection = rekognition.CfnCollection(
            self,
            "PPECollection",
            collection_id=f"{self._lab_name}-ppe-collection",
        )
        
        # SNS Topic for safety alerts
        self.notification_topic = sns.Topic(
            self,
            "NotificationTopic",
            topic_name=f"{self._lab_name}-safety-alerts",
            display_name="SafetyVision Pro - Safety Alerts",
        )
        
        # Email subscription (optional - for demo purposes)
        # In production, you would configure this properly
        self.email_subscription = sns.Subscription(
            self,
            "EmailSubscription",
            topic=self.notification_topic,
            endpoint="safety-alerts@example.com",  # Replace with actual email
            protocol=sns.SubscriptionProtocol.EMAIL,
        )
        
        # IAM Role for Rekognition to publish to SNS
        self.rekognition_sns_role = iam.Role(
            self,
            "RekognitionSNSRole",
            role_name=f"{self._lab_name}-rekognition-sns-role",
            assumed_by=iam.ServicePrincipal("rekognition.amazonaws.com"),
            inline_policies={
                "SNSPublish": iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            effect=iam.Effect.ALLOW,
                            actions=[
                                "sns:Publish",
                            ],
                            resources=[self.notification_topic.topic_arn],
                        )
                    ]
                )
            }
        )
        
        # Custom Labels Configuration for PPE
        # Note: In a real implementation, you would train custom models
        # For this demo, we'll use the built-in DetectProtectiveEquipment
        
        # Create a project for custom labels (optional)
        self.ppe_project = rekognition.CfnProject(
            self,
            "PPEProject",
            project_name=f"{self._lab_name}-ppe-detection",
        )
        
        # Outputs
        CfnOutput(self, "PPECollectionId", value=self.ppe_collection.collection_id)
        CfnOutput(self, "NotificationTopicArn", value=self.notification_topic.topic_arn)
        CfnOutput(self, "PPEProjectArn", value=self.ppe_project.attr_arn)
        
        # Store configuration in Parameter Store for easy access
        from aws_cdk import aws_ssm as ssm
        
        ssm.StringParameter(
            self,
            "PPECollectionIdParameter",
            parameter_name=f"/safety-vision/{self._lab_name}/ppe-collection-id",
            string_value=self.ppe_collection.collection_id,
            description="PPE Collection ID for Rekognition",
        )
        
        ssm.StringParameter(
            self,
            "SNSTopicArnParameter",
            parameter_name=f"/safety-vision/{self._lab_name}/sns-topic-arn",
            string_value=self.notification_topic.topic_arn,
            description="SNS Topic ARN for safety alerts",
        )
