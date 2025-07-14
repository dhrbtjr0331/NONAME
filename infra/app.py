#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infra.infra_stack import InfraStack


app = cdk.App()

# Get environment variables
account = os.getenv('CDK_DEFAULT_ACCOUNT')
region = os.getenv('CDK_DEFAULT_REGION', 'us-east-1')
environment = os.getenv('ENVIRONMENT', 'dev')

# Validate environment
valid_environments = ['dev', 'staging', 'prod']
if environment not in valid_environments:
    raise ValueError(f"Invalid environment: {environment}. Must be one of {valid_environments}")

print(f"🚀 Deploying to environment: {environment}")
print(f"📍 Account: {account}, Region: {region}")

InfraStack(app, f"B2BMarketplace-{environment}", 
    env=cdk.Environment(account=account, region=region),
    deployment_env=environment,
    description=f"B2B Marketplace Platform Infrastructure - {environment.upper()}"
)

app.synth()
