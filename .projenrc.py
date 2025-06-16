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
        "aiosqlite>=0.19.0",
        "alembic>=1.12.0",
        "greenlet>=2.0.0",
        
        # Validation & Settings
        "pydantic[email]>=2.5.0",
        "pydantic-settings>=2.1.0",
    ],
    dev_deps=[
        "pytest>=7.4.0",
        "pytest-asyncio>=0.21.0",
        "httpx>=0.25.0",
        "black>=23.0.0",
        "flake8>=6.0.0",
        "mypy>=1.7.0",
    ]
)

project.synth()