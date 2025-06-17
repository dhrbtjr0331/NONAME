from projen.python import PythonProject

project = PythonProject(
    author_email="dhrbtjr0331@gmail.com",
    author_name="Carrick Oh",
    module_name="marketplace_platform",
    name="marketplace-platform",
    version="0.1.0",
    deps=[
        # FastAPI and server
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        
        # Authentication & Security
        "python-jose[cryptography]>=3.3.0",
        "passlib[bcrypt]>=1.7.4",
        "python-multipart>=0.0.6",
        
        # Database
        "sqlalchemy>=2.0.0",
        "asyncpg>=0.29.0",           # ADD: PostgreSQL async driver
        "alembic>=1.12.0",
        "greenlet>=2.0.0",
        
        # Validation & Settings
        "pydantic[email]>=2.5.0",
        "pydantic-settings>=2.1.0",
        
        # HTTP Client (for inter-service communication)
        "httpx>=0.25.0",             # ADD: For calling other microservices
        
        # Email notifications
        "boto3>=1.34.0",             # ADD: For AWS SES
        "botocore>=1.34.0",          # ADD: AWS core library
        
        # Background tasks (for async email sending)
        "celery>=5.3.0",             # ADD: Task queue
        "redis>=5.0.0",              # ADD: Celery broker
        
        # Logging and monitoring
        "structlog>=23.2.0",         # ADD: Better logging
        
        # Date/time handling
        "python-dateutil>=2.8.0",   # ADD: Date utilities
    ],
    dev_deps=[
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.25.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.7.0",
        
        # Additional testing tools
        "pytest-mock>=3.12.0",      # ADD: Mocking for tests
        "factory-boy>=3.3.0",       # ADD: Test data factories
        "faker>=20.0.0",             # ADD: Fake data generation
    ]
)

project.synth()