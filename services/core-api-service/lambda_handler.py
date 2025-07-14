import json
import os
import boto3
from typing import Dict, Any
from mangum import Mangum

# Global variables for caching secrets and connections
_db_credentials = None
_jwt_secret = None

def is_lambda_environment():
    """Check if running in AWS Lambda"""
    return bool(os.environ.get('AWS_LAMBDA_FUNCTION_NAME'))

def is_local_testing():
    """Check if running locally for testing Lambda code"""
    return not is_lambda_environment() and __name__ == "__main__"

async def get_secret(secret_arn: str) -> Dict[str, Any]:
    """Retrieve secret from AWS Secrets Manager"""
    try:
        session = boto3.Session()
        client = session.client('secretsmanager')
        response = client.get_secret_value(SecretId=secret_arn)
        return json.loads(response['SecretString'])
    except Exception as e:
        print(f"Error retrieving secret {secret_arn}: {e}")
        raise

def setup_local_testing_environment():
    """Set up environment variables for local testing of Lambda code"""
    print("🧪 Setting up local testing environment for Lambda...")
    
    # Set local testing environment variables
    os.environ.update({
        'ENVIRONMENT': 'local_lambda_test',
        'PROJECT_NAME': 'B2B Marketplace API (Lambda Test)',
        'DEBUG': 'true',
        'BACKEND_CORS_ORIGINS': '["http://localhost:3000", "http://127.0.0.1:3000"]',
        
        # Use SQLite for local Lambda testing
        'DATABASE_URL': 'sqlite+aiosqlite:///./test_lambda.db',
        
        # Local JWT settings
        'SECRET_KEY': 'test_jwt_secret_for_lambda_testing_only',
        'ALGORITHM': 'HS256',
        'ACCESS_TOKEN_EXPIRE_MINUTES': '30',
    })
    
    print("✅ Local testing environment configured")

async def setup_aws_environment():
    """Set up environment variables from AWS Secrets Manager"""
    global _db_credentials, _jwt_secret
    
    try:
        print("☁️ Setting up AWS environment...")
        
        # Get database credentials
        if not _db_credentials:
            db_secret_arn = os.environ['DATABASE_SECRET_ARN']
            _db_credentials = await get_secret(db_secret_arn)
            
            # Set database URL environment variable
            database_url = (
                f"postgresql+asyncpg://{_db_credentials['username']}:"
                f"{_db_credentials['password']}@{_db_credentials['host']}:"
                f"{_db_credentials['port']}/{os.environ['DATABASE_NAME']}"
            )
            os.environ['DATABASE_URL'] = database_url
            print("✅ Database URL configured from Secrets Manager")
        
        # Get JWT secret
        if not _jwt_secret:
            jwt_secret_arn = os.environ['JWT_SECRET_ARN']
            jwt_data = await get_secret(jwt_secret_arn)
            _jwt_secret = jwt_data['secret_key']
            
            # Set JWT environment variables
            os.environ['SECRET_KEY'] = _jwt_secret
            os.environ['ALGORITHM'] = jwt_data.get('algorithm', 'HS256')
            print("✅ JWT secret configured from Secrets Manager")
            
        # Set other AWS-specific environment variables
        os.environ.update({
            'ENVIRONMENT': 'production',
            'PROJECT_NAME': 'B2B Marketplace API',
            'DEBUG': 'false',
            'BACKEND_CORS_ORIGINS': '["*"]',  # Configure properly for production
        })
        
        print("✅ AWS environment setup completed")
        
    except Exception as e:
        print(f"Error setting up AWS environment: {e}")
        raise

# Import your existing FastAPI app after environment setup
async def get_app():
    """Get the FastAPI app with proper configuration"""
    
    if is_lambda_environment():
        # Running in AWS Lambda
        await setup_aws_environment()
    elif is_local_testing():
        # Running locally for Lambda testing
        setup_local_testing_environment()
    else:
        # Running in some other context, use environment as-is
        print("ℹ️ Using existing environment configuration")
    
    # Now import your existing FastAPI app
    from app.main import app
    return app

# Lambda handler for AWS
async def lambda_handler(event, context):
    """Lambda handler that sets up environment and delegates to Mangum"""
    try:
        app = await get_app()
        mangum_handler = Mangum(app, lifespan="off")
        return mangum_handler(event, context)
    except Exception as e:
        print(f"Lambda handler error: {e}")
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type, Authorization",
            },
            "body": json.dumps({"error": "Internal server error", "detail": str(e)})
        }

# For AWS Lambda runtime
handler = lambda_handler

# Test function for local development
if __name__ == "__main__":
    import asyncio
    import uvicorn
    
    async def run_local():
        """Run the app locally for testing"""
        print("🚀 Starting Lambda code in local testing mode...")
        app = await get_app()
        return app
    
    # Run locally
    try:
        app = asyncio.run(run_local())
        print("🌐 Starting server on http://localhost:8001")
        print("📝 This is Lambda code running locally with SQLite for testing")
        print("🔄 Use this to test Lambda-specific features before deployment")
        uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
    except Exception as e:
        print(f"❌ Error running locally: {e}")
        print("💡 This is expected if you haven't set up the local environment properly")
        print("🔧 Try running from the local development environment instead:")
        print("   python run_core_api.py")