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
- Lambda deployment configuration

## Common Development Commands

### Frontend Development
```bash
cd frontend
npm start          # Start development server on port 3000
npm run build      # Build for production
npm test           # Run React tests
```

### Backend Development
```bash
# Run core API service locally
python run_core_api.py     # Starts on port 8000 with hot reload

# Test Lambda adapter locally
cd services/core-api-service
python lambda_handler.py  # Starts on port 8001 for Lambda testing
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
- SQLite for development (`test.db`, `test_lambda.db`)
- Alembic for migrations

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