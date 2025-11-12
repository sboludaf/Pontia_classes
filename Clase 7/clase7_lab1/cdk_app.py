#!/usr/bin/env python3
"""
Seguridad Obra Lab - CDK Application
Despliega toda la infraestructura del laboratorio de seguridad con AWS Rekognition
"""

import os
import sys
import aws_cdk as cdk
from stacks.seguridad_obra_stack import SeguridadObraStack

app = cdk.App()

# Obtener configuración desde contexto
lab_name = app.node.try_get_context("lab_name") or "seguridad-obra-lab"
region = app.node.try_get_context("region") or "eu-west-1"

# Crear el stack principal
SeguridadObraStack(
    app,
    f"{lab_name}-stack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=region
    ),
    description=f"Laboratorio de Seguridad con AWS Rekognition - {lab_name}",
    lab_name=lab_name,
    region=region
)

app.synth()
