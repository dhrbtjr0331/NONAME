# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a B2B marketplace application with a React frontend and FastAPI backend services. The project consists of microservices for core API functionality and notifications, along with AWS infrastructure deployment using CDK.

## Architecture

### Frontend
- React 18 application located in `frontend/` 
- Uses React Router for navigation, axios for API calls, and react-hook-form for forms
- Components organized by feature: auth, manufacturer, supplier, shared
- Service layer abstracts API calls in `frontend/src/services/`

### Backend Services
- **Core API Service**: Main backend API (`services/core-api-service/`)
  - Contains both local development and Lambda deployment code
  - `lambda_handler.py` provides AWS Lambda adapter using Mangum
- **Notification Service**: Email notifications (`services/notification-service/`)

All services use FastAPI with SQLAlchemy, async/await patterns, and JWT authentication.

### Infrastructure
- AWS CDK for infrastructure as code (`infra/`)
- Multi-tier serverless architecture on AWS
- Environment-specific configurations (dev/staging/prod)

## Common Development Commands

### Frontend Development
```bash
cd frontend
npm start          # Start development server on port 3000
npm run build      # Build for production
npm test           # Run React tests with Jest
npm test -- --coverage  # Run tests with coverage report
```

### Backend Development
```bash
# Run core API service locally (from project root)
python run_core_api.py     # Starts on port 8000 with hot reload

# Test Lambda adapter locally
cd services/core-api-service
python lambda_handler.py  # Starts on port 8001 for Lambda testing

# Run Python tests
pytest tests/             # Run all tests
pytest tests/test_example.py  # Run specific test file
pytest -v                 # Verbose test output

# Code quality
black .                   # Format Python code
flake8 .                  # Lint Python code
mypy .                    # Type checking
```

### Infrastructure
```bash
cd infra
pip install -r requirements.txt

# Multi-environment deployment
ENVIRONMENT=dev cdk deploy        # Deploy to development
ENVIRONMENT=staging cdk deploy    # Deploy to staging  
ENVIRONMENT=prod cdk deploy       # Deploy to production

# Other commands
cdk synth          # Generate CloudFormation templates
cdk diff           # Show changes before deployment
cdk destroy        # Delete stack (add ENVIRONMENT= for specific env)
```

## Key Architecture Patterns

### Service Structure
Each backend service follows FastAPI best practices:
- `main.py` - FastAPI app initialization
- `routers/` - API endpoints grouped by feature
- `services/` - Business logic layer
- `models/` - SQLAlchemy database models
- `schemas/` - Pydantic request/response models
- `config/` - Database and settings configuration

### Authentication Flow
- JWT-based authentication implemented in `utils/jwt_handler.py`
- Protected routes use `dependencies/auth.py` for token validation
- User management in `services/auth_service.py`

### Database
- SQLAlchemy with async support
- SQLite for development (`shared/database/test.db`, `test_lambda.db`)
- PostgreSQL for production (RDS Aurora Serverless v2)
- Database sessions managed via dependency injection
- Models use declarative base with proper relationships

## Deployment Architecture

### Single Codebase with Deployment Adapters
- Single source of truth in `services/core-api-service/`
- `app/main.py` contains the FastAPI application
- `lambda_handler.py` provides AWS Lambda adapter using Mangum
- CDK builds Lambda deployment from the same service code
- Environment-specific configuration handled automatically

### Multi-Environment Support
The infrastructure supports three environments with different configurations:

**Development (`dev`)**:
- Minimal resources for cost efficiency
- No deletion protection
- Short log retention (3 days)

**Staging (`staging`)**:
- Mid-tier resources for realistic testing
- No deletion protection
- Medium log retention (1 week)

**Production (`prod`)**:
- High-performance resources
- Deletion protection enabled
- Extended log retention (1 month)

Stack names: `B2BMarketplace-dev`, `B2BMarketplace-staging`, `B2BMarketplace-prod`

## AWS Infrastructure Architecture

### Core AWS Services Used

**Compute & API:**
- **AWS Lambda**: Python 3.12 runtime for backend API (FastAPI via Mangum adapter)
- **API Gateway**: REST API with Lambda proxy integration and CORS support
- **CloudWatch Logs**: Environment-specific retention (3 days dev, 1 week staging, 1 month prod)

**Database:**
- **RDS Aurora Serverless v2**: PostgreSQL 15.4 with auto-scaling
  - Dev: 0.5-2 ACUs | Staging: 0.5-4 ACUs | Prod: 1-8 ACUs
- **AWS Secrets Manager**: Auto-generated database credentials with rotation

**Frontend Hosting:**
- **S3**: Static website hosting for React application
- **CloudFront**: CDN with HTTPS enforcement and SPA routing support

**Security & Access:**
- **IAM Roles**: Least-privilege access for Lambda functions
- **Secrets Manager**: JWT secrets and database credentials
- **Security Groups**: Network-level access control

### Network Architecture

**VPC Configuration** (`10.0.0.0/16` across 2 AZs):
- **Public Subnets** (`10.0.0.0/24`, `10.0.1.0/24`): NAT Gateways, Internet Gateway
- **Private Subnets** (`10.0.32.0/24`, `10.0.33.0/24`): Lambda functions with internet access
- **Database Subnets** (`10.0.64.0/24`, `10.0.65.0/24`): Isolated RDS cluster
- **S3 VPC Endpoint**: Direct S3 access without internet routing

**Security Groups:**
- Lambda functions can only access database on port 5432
- Database accepts connections only from Lambda security group
- Outbound internet access via NAT Gateways for private subnets

### Environment-Specific Configurations

**Production Safeguards:**
- Deletion protection enabled for RDS
- RETAIN removal policy for critical resources
- Extended log retention (1 month)
- Higher resource allocations

**Development Flexibility:**
- DESTROY removal policy for easy cleanup
- Minimal resource allocations for cost efficiency
- Short log retention for reduced storage costs

### Secret Management

**Automated Secret Handling:**
- Database credentials auto-generated and stored in Secrets Manager
- JWT secrets (64-char random strings) with algorithm specifications
- Lambda environment variables reference secret ARNs
- No hardcoded credentials in codebase

### API Documentation Access

FastAPI automatic documentation available at:
- **Local Dev**: http://localhost:8000/docs
- **Lambda Test**: http://localhost:8001/docs  
- **Deployed**: `{API_Gateway_URL}/docs`

## Testing Strategy

### Frontend Testing
- Jest and React Testing Library for component tests
- Tests located alongside components or in `__tests__` directories
- Coverage reports available via `npm test -- --coverage`

### Backend Testing
- pytest for Python testing with async support
- Factory Boy for test data generation
- Test fixtures and parametrized tests
- Run tests from project root with `pytest tests/`

## Development Database Setup

The project uses different databases for different contexts:
- **Local Development**: SQLite at `shared/database/test.db` (shared across services)
- **Lambda Testing**: SQLite at `services/core-api-service/test_lambda.db` (isolated)
- **Production**: PostgreSQL via RDS Aurora Serverless v2

Database URL configuration is handled through settings, with automatic table creation on startup.

