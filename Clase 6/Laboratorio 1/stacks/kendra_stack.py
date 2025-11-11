"""
Kendra Stack - Kendra Index + Data Source
Crea el índice de Kendra y la fuente de datos S3
"""

import aws_cdk as cdk
from aws_cdk import (
    aws_kendra as kendra,
    aws_s3 as s3,
    aws_iam as iam,
)
from constructs import Construct


class KendraStack(cdk.Stack):
    """Stack para Kendra Index"""
    
    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lab_name: str,
        documents_bucket: s3.Bucket,
        kendra_role: iam.Role,
        **kwargs
    ):
        super().__init__(scope, construct_id, **kwargs)
        
        self.lab_name = lab_name
        
        # ==================== KENDRA INDEX ====================
        self.kendra_index = kendra.CfnIndex(
            self,
            "KendraIndex",
            name=f"{lab_name}-index",
            edition="DEVELOPER_EDITION",
            role_arn=kendra_role.role_arn,
            description="Índice Kendra para RAG Lab",
        )
        
        self.kendra_index_id = self.kendra_index.ref
        self.kendra_index_arn = self.kendra_index.attr_arn
        
        # ==================== DATA SOURCE (S3) ====================
        self.data_source = kendra.CfnDataSource(
            self,
            "S3DataSource",
            name=f"{lab_name}-s3-source",
            index_id=self.kendra_index_id,
            type="S3",
            role_arn=kendra_role.role_arn,
            data_source_configuration=kendra.CfnDataSource.DataSourceConfigurationProperty(
                s3_configuration=kendra.CfnDataSource.S3DataSourceConfigurationProperty(
                    bucket_name=documents_bucket.bucket_name,
                    inclusion_prefixes=["documents/"],
                )
            ),
            schedule="cron(0 */6 * * ? *)",  # Cada 6 horas
            description="Fuente de datos S3 para documentos",
        )
        
        # Agregar dependencia explícita
        self.data_source.add_dependency(self.kendra_index)
        
        # ==================== OUTPUTS ====================
        cdk.CfnOutput(
            self,
            "KendraIndexId",
            value=self.kendra_index_id,
            export_name=f"{lab_name}-kendra-index-id",
        )
        
        cdk.CfnOutput(
            self,
            "KendraIndexArn",
            value=self.kendra_index_arn,
            export_name=f"{lab_name}-kendra-index-arn",
        )
        
        cdk.CfnOutput(
            self,
            "DataSourceId",
            value=self.data_source.ref,
            export_name=f"{lab_name}-data-source-id",
        )
