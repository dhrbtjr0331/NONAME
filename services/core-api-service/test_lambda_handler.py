import pytest
import asyncio
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock
from lambda_handler import (
    is_lambda_environment, 
    is_local_testing, 
    setup_local_testing_environment,
    setup_aws_environment,
    get_app,
    lambda_handler,
    get_secret
)


class TestEnvironmentDetection:
    """Test environment detection functions"""
    
    def test_is_lambda_environment_true(self):
        """Test Lambda environment detection when AWS_LAMBDA_FUNCTION_NAME is set"""
        with patch.dict(os.environ, {'AWS_LAMBDA_FUNCTION_NAME': 'test-function'}):
            assert is_lambda_environment() is True
    
    def test_is_lambda_environment_false(self):
        """Test Lambda environment detection when AWS_LAMBDA_FUNCTION_NAME is not set"""
        with patch.dict(os.environ, {}, clear=True):
            assert is_lambda_environment() is False
    
    def test_is_local_testing_true(self):
        """Test local testing detection"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('lambda_handler.__name__', '__main__'):
                assert is_local_testing() is True
    
    def test_is_local_testing_false_in_lambda(self):
        """Test local testing detection returns False in Lambda environment"""
        with patch.dict(os.environ, {'AWS_LAMBDA_FUNCTION_NAME': 'test-function'}):
            with patch('lambda_handler.__name__', '__main__'):
                assert is_local_testing() is False


class TestEnvironmentSetup:
    """Test environment setup functions"""
    
    def test_setup_local_testing_environment(self):
        """Test local testing environment setup"""
        with patch.dict(os.environ, {}, clear=True):
            setup_local_testing_environment()
            
            assert os.environ['ENVIRONMENT'] == 'local_lambda_test'
            assert os.environ['PROJECT_NAME'] == 'B2B Marketplace API (Lambda Test)'
            assert os.environ['DEBUG'] == 'true'
            assert os.environ['DATABASE_URL'] == 'sqlite+aiosqlite:///./test_lambda.db'
            assert os.environ['SECRET_KEY'] == 'test_jwt_secret_for_lambda_testing_only'
    
    @pytest.mark.asyncio
    async def test_get_secret_success(self):
        """Test successful secret retrieval"""
        mock_client = MagicMock()
        mock_client.get_secret_value.return_value = {
            'SecretString': '{"secret_key": "test-secret", "algorithm": "HS256"}'
        }
        
        with patch('boto3.Session') as mock_session:
            mock_session.return_value.client.return_value = mock_client
            
            result = await get_secret('test-secret-arn')
            
            assert result == {"secret_key": "test-secret", "algorithm": "HS256"}
            mock_client.get_secret_value.assert_called_once_with(SecretId='test-secret-arn')
    
    @pytest.mark.asyncio
    async def test_get_secret_failure(self):
        """Test secret retrieval failure"""
        mock_client = MagicMock()
        mock_client.get_secret_value.side_effect = Exception("Secret not found")
        
        with patch('boto3.Session') as mock_session:
            mock_session.return_value.client.return_value = mock_client
            
            with pytest.raises(Exception, match="Secret not found"):
                await get_secret('test-secret-arn')
    
    @pytest.mark.asyncio
    async def test_setup_aws_environment(self):
        """Test AWS environment setup"""
        # Mock database credentials
        db_credentials = {
            'username': 'testuser',
            'password': 'testpass',
            'host': 'test-host.rds.amazonaws.com',
            'port': '5432'
        }
        
        # Mock JWT secret
        jwt_secret = {
            'secret_key': 'test-jwt-secret',
            'algorithm': 'HS256'
        }
        
        with patch.dict(os.environ, {
            'DATABASE_SECRET_ARN': 'db-secret-arn',
            'JWT_SECRET_ARN': 'jwt-secret-arn',
            'DATABASE_NAME': 'test_db'
        }):
            with patch('lambda_handler.get_secret') as mock_get_secret:
                # Setup mock to return different values based on ARN
                def side_effect(arn):
                    if arn == 'db-secret-arn':
                        return db_credentials
                    elif arn == 'jwt-secret-arn':
                        return jwt_secret
                    else:
                        raise ValueError(f"Unknown ARN: {arn}")
                
                mock_get_secret.side_effect = side_effect
                
                await setup_aws_environment()
                
                # Check database URL was set correctly
                expected_db_url = (
                    "postgresql+asyncpg://testuser:testpass@"
                    "test-host.rds.amazonaws.com:5432/test_db"
                )
                assert os.environ['DATABASE_URL'] == expected_db_url
                
                # Check JWT settings were set
                assert os.environ['SECRET_KEY'] == 'test-jwt-secret'
                assert os.environ['ALGORITHM'] == 'HS256'
                assert os.environ['ENVIRONMENT'] == 'production'


class TestGetApp:
    """Test get_app function"""
    
    @pytest.mark.asyncio
    async def test_get_app_lambda_environment(self):
        """Test get_app in Lambda environment"""
        with patch.dict(os.environ, {'AWS_LAMBDA_FUNCTION_NAME': 'test-function'}):
            with patch('lambda_handler.setup_aws_environment') as mock_setup_aws:
                with patch('app.main.app') as mock_app:
                    result = await get_app()
                    
                    mock_setup_aws.assert_called_once()
                    assert result == mock_app
    
    @pytest.mark.asyncio
    async def test_get_app_local_testing(self):
        """Test get_app in local testing environment"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('lambda_handler.__name__', '__main__'):
                with patch('lambda_handler.setup_local_testing_environment') as mock_setup_local:
                    with patch('app.main.app') as mock_app:
                        result = await get_app()
                        
                        mock_setup_local.assert_called_once()
                        assert result == mock_app
    
    @pytest.mark.asyncio
    async def test_get_app_other_environment(self):
        """Test get_app in other environment (neither Lambda nor local testing)"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('lambda_handler.__name__', 'not_main'):
                with patch('app.main.app') as mock_app:
                    result = await get_app()
                    
                    assert result == mock_app


class TestLambdaHandler:
    """Test lambda_handler function"""
    
    @pytest.mark.asyncio
    async def test_lambda_handler_success(self):
        """Test successful lambda handler execution"""
        mock_event = {'httpMethod': 'GET', 'path': '/health'}
        mock_context = MagicMock()
        mock_app = MagicMock()
        mock_response = {'statusCode': 200, 'body': '{"status": "healthy"}'}
        
        with patch('lambda_handler.get_app', return_value=mock_app):
            with patch('lambda_handler.Mangum') as mock_mangum_class:
                mock_mangum_instance = MagicMock()
                mock_mangum_instance.return_value = mock_response
                mock_mangum_class.return_value = mock_mangum_instance
                
                result = await lambda_handler(mock_event, mock_context)
                
                assert result == mock_response
                mock_mangum_class.assert_called_once_with(mock_app, lifespan="off")
                mock_mangum_instance.assert_called_once_with(mock_event, mock_context)
    
    @pytest.mark.asyncio
    async def test_lambda_handler_error(self):
        """Test lambda handler error handling"""
        mock_event = {'httpMethod': 'GET', 'path': '/health'}
        mock_context = MagicMock()
        
        with patch('lambda_handler.get_app', side_effect=Exception("Test error")):
            result = await lambda_handler(mock_event, mock_context)
            
            assert result['statusCode'] == 500
            assert 'error' in json.loads(result['body'])
            assert 'Internal server error' in json.loads(result['body'])['error']
            
            # Check CORS headers are present
            assert result['headers']['Access-Control-Allow-Origin'] == '*'
            assert 'GET, POST, PUT, DELETE, OPTIONS' in result['headers']['Access-Control-Allow-Methods']


class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_local_lambda_simulation(self):
        """Test running Lambda handler in local simulation mode"""
        with patch.dict(os.environ, {}, clear=True):
            with patch('lambda_handler.__name__', '__main__'):
                # Mock the FastAPI app import to avoid database dependencies
                with patch('app.main.app') as mock_app:
                    
                    # Test event similar to API Gateway
                    test_event = {
                        'httpMethod': 'GET',
                        'path': '/health',
                        'headers': {},
                        'body': None
                    }
                    test_context = MagicMock()
                    
                    with patch('lambda_handler.Mangum') as mock_mangum_class:
                        mock_mangum_instance = MagicMock()
                        mock_response = {
                            'statusCode': 200,
                            'body': json.dumps({'status': 'healthy'})
                        }
                        mock_mangum_instance.return_value = mock_response
                        mock_mangum_class.return_value = mock_mangum_instance
                        
                        result = await lambda_handler(test_event, test_context)
                        
                        # Verify environment was set up for local testing
                        assert os.environ['ENVIRONMENT'] == 'local_lambda_test'
                        assert os.environ['DATABASE_URL'] == 'sqlite+aiosqlite:///./test_lambda.db'
                        
                        # Verify response
                        assert result == mock_response
                        assert result['statusCode'] == 200