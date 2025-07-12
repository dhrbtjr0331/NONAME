from aws_cdk import (
    Stack,
    Duration,
    CfnOutput,
    RemovalPolicy,
    aws_lambda as _lambda,
    aws_apigateway as apigateway,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    aws_s3 as s3,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_iam as iam,
    aws_logs as logs,
)
from constructs import Construct
import json

class InfraStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create VPC for the application
        self.vpc = self.create_vpc()

        # Create RDS Aurora Serverless v2 cluster
        self.database = self.create_database()

        # Create Secrets Manager for application secrets
        self.secrets = self.create_secrets()

        # Create Core API Lambda function
        self.core_api_lambda = self.create_core_api_lambda()
        
        # Create API Gateway
        self.api_gateway = self.create_api_gateway()

        # Create S3 bucket for frontend hosting
        self.frontend_bucket = self.create_frontend_hosting()

        # Create CloudFront distriubtion for the frontend
        self.cloudfront = self.create_cloudfront_distribution()

        # Output important values
        self.create_outputs()

    def create_vpc(self) -> ec2.Vpc:
        """Create VPC with public and private subnets"""
        vpc = ec2.Vpc(self, "MarketplaceVpc",
            max_azs=2,
            ip_addresses=ec2.IpAddresses.cidr("10.0.0.0/16"),
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="Public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Private",
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS,
                    cidr_mask=24
                ),
                ec2.SubnetConfiguration(
                    name="Database",
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED,
                    cidr_mask=24
                )
            ]
        )

        vpc.add_gateway_endpoint(
            "S3Endpoint",
            service=ec2.GatewayVpcEndpointAwsService.S3,
        )

        return vpc

    def create_database(self) -> rds.DatabaseCluster:
        """Create RDS Aurora Serverless v2 PostgreSQL cluster"""
        
        # Create subnet group for RDS
        db_subnet_group = rds.SubnetGroup(
            self, "DatabaseSubnetGroup",
            description="Subnet group for B2B Marketplace database",
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_ISOLATED
            ),
        )
        
        # Create security group for database
        db_security_group = ec2.SecurityGroup(
            self, "DatabaseSecurityGroup",
            vpc=self.vpc,
            description="Security group for B2B Marketplace database",
            allow_all_outbound=False,
        )
        
        # Create Aurora Serverless v2 cluster
        cluster = rds.DatabaseCluster(
            self, "DatabaseCluster",
            engine=rds.DatabaseClusterEngine.aurora_postgres(
                version=rds.AuroraPostgresEngineVersion.VER_15_4
            ),
            credentials=rds.Credentials.from_generated_secret(
                "b2b_marketplace_db_admin",
                secret_name="b2b-marketplace/database/credentials"
            ),
            default_database_name="b2b_marketplace",
            vpc=self.vpc,
            subnet_group=db_subnet_group,
            security_groups=[db_security_group],
            serverless_v2_min_capacity=0.5,
            serverless_v2_max_capacity=4,
            enable_data_api=True,  # Enable Data API for serverless access
            deletion_protection=False,  # Set to True in production
            removal_policy=RemovalPolicy.DESTROY,  # Change in production
        )
        
        return cluster
    
    def create_secrets(self):
        """Create secrets for JWT and other application secrets"""
        
        # JWT Secret
        jwt_secret = secretsmanager.Secret(
            self, "JwtSecret",
            description="JWT secret key for B2B Marketplace",
            secret_name="b2b-marketplace/jwt-secret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                secret_string_template=json.dumps({"algorithm": "HS256"}),
                generate_string_key="secret_key",
                exclude_characters=' \t\n\r\f\v"\\',
                password_length=64,
            ),
        )
        
        return {"jwt": jwt_secret}
    
    def create_core_api_lambda(self):
        """Create the Core API Lambda function"""
        
        # Create security group for Lambda
        lambda_security_group = ec2.SecurityGroup(
            self, "LambdaSecurityGroup",
            vpc=self.vpc,
            description="Security group for Lambda functions",
            allow_all_outbound=True,
        )
        
        # Allow Lambda to connect to database
        self.database.connections.allow_from(
            lambda_security_group,
            ec2.Port.tcp(5432),
            "Lambda to RDS connection"
        )
        
        # Create Lambda execution role
        lambda_role = iam.Role(
            self, "CoreApiLambdaRole",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSLambdaVPCAccessExecutionRole"
                ),
            ],
        )
        
        # Grant access to secrets
        self.secrets["jwt"].grant_read(lambda_role)
        self.database.secret.grant_read(lambda_role)
        
        # Create Lambda function
        core_api_lambda = _lambda.Function(
            self, "CoreApiLambda",
            runtime=_lambda.Runtime.PYTHON_3_12,
            handler="main.handler",
            code=_lambda.Code.from_asset("lambda/core-api"),  # You'll create this directory
            vpc=self.vpc,
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            security_groups=[lambda_security_group],
            role=lambda_role,
            timeout=Duration.seconds(30),
            memory_size=512,
            environment={
                "DATABASE_SECRET_ARN": self.database.secret.secret_arn,
                "JWT_SECRET_ARN": self.secrets["jwt"].secret_arn,
                "DATABASE_NAME": "b2b_marketplace",
            },
            log_retention=logs.RetentionDays.ONE_WEEK,
        )
        
        return core_api_lambda
    
    def create_api_gateway(self):
        """Create API Gateway for the Lambda functions"""
        
        # Create REST API
        api = apigateway.RestApi(
            self, "B2bMarketplaceApi",
            rest_api_name="B2B Marketplace API",
            description="API Gateway for B2B Marketplace Platform",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,  # Restrict in production
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"],
            ),
            binary_media_types=["*/*"],
        )
        
        # Create Lambda integration
        core_api_integration = apigateway.LambdaIntegration(
            self.core_api_lambda,
            proxy=True,
        )
        
        # Add proxy resource to capture all paths
        api.root.add_proxy(
            default_integration=core_api_integration,
            any_method=True,
        )
        
        return api

    def create_frontend_hosting(self):
        """Create S3 bucket for frontend hosting"""
        
        bucket = s3.Bucket(
            self, "FrontendBucket",
            website_index_document="index.html",
            website_error_document="error.html",
            public_read_access=True,
            block_public_access=s3.BlockPublicAccess(
                block_public_acls=False,
                block_public_policy=False,
                ignore_public_acls=False,
                restrict_public_buckets=False,
            ),
            removal_policy=RemovalPolicy.DESTROY,  # Change in production
        )
        
        return bucket
    
    def create_cloudfront_distribution(self):
        """Create CloudFront distribution for frontend"""
        
        distribution = cloudfront.Distribution(
            self, "FrontendDistribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(self.frontend_bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
            ),
            default_root_object="index.html",
            error_responses=[
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=200,
                    response_page_path="/index.html",  # For SPA routing
                ),
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=200,
                    response_page_path="/index.html",  # For SPA routing
                ),
            ],
        )
        
        return distribution

    def create_outputs(self):
        """Create CloudFormation outputs"""
        
        CfnOutput(
            self, "ApiGatewayUrl",
            value=self.api_gateway.url,
            description="API Gateway URL",
        )
        
        CfnOutput(
            self, "DatabaseEndpoint",
            value=self.database.cluster_endpoint.hostname,
            description="RDS Aurora cluster endpoint",
        )
        
        CfnOutput(
            self, "DatabaseSecretArn",
            value=self.database.secret.secret_arn,
            description="Database credentials secret ARN",
        )
        
        CfnOutput(
            self, "JwtSecretArn",
            value=self.secrets["jwt"].secret_arn,
            description="JWT secret ARN",
        )
        
        CfnOutput(
            self, "FrontendBucketName",
            value=self.frontend_bucket.bucket_name,
            description="S3 bucket name for frontend hosting",
        )
        
        CfnOutput(
            self, "CloudFrontUrl",
            value=f"https://{self.cloudfront.distribution_domain_name}",
            description="CloudFront distribution URL",
        )
        
        CfnOutput(
            self, "VpcId",
            value=self.vpc.vpc_id,
            description="VPC ID",
        )