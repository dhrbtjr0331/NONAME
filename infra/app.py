#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infra.infra_stack import InfraStack


app = cdk.App()

# Get environment variables
account = os.getenv('CDK_DEFAULT_ACCOUNT')
region = os.getenv('CDK_DEFAULT_REGION', 'us-east-1')


InfraStack(app, "InfraStack", 
    env=cdk.Environment(account=account, region=region),
    description="B2B Marketplace Platform Infrastructure"
)

app.synth()
