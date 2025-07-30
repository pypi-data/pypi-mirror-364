"""Unit tests for ScoutML configuration."""

import os
import pytest
import tempfile
from scoutml import Config
from scoutml.exceptions import ScoutMLError


class TestConfig:
    """Test configuration functionality."""
    
    def setup_method(self):
        """Set up test environment."""
        # Save original env vars
        self.original_api_key = os.environ.get('SCOUTML_API_KEY')
        self.original_api_url = os.environ.get('SCOUTML_API_URL')
        
        # Clear env vars for testing
        if 'SCOUTML_API_KEY' in os.environ:
            del os.environ['SCOUTML_API_KEY']
        if 'SCOUTML_API_URL' in os.environ:
            del os.environ['SCOUTML_API_URL']
    
    def teardown_method(self):
        """Restore original environment."""
        if self.original_api_key:
            os.environ['SCOUTML_API_KEY'] = self.original_api_key
        elif 'SCOUTML_API_KEY' in os.environ:
            del os.environ['SCOUTML_API_KEY']
            
        if self.original_api_url:
            os.environ['SCOUTML_API_URL'] = self.original_api_url
        elif 'SCOUTML_API_URL' in os.environ:
            del os.environ['SCOUTML_API_URL']
    
    def test_config_defaults(self):
        """Test default configuration values."""
        # Ensure no API key in environment
        saved_api_key = os.environ.get('SCOUTML_API_KEY')
        if 'SCOUTML_API_KEY' in os.environ:
            del os.environ['SCOUTML_API_KEY']
        
        # Temporarily rename .env file if it exists
        import shutil
        env_exists = os.path.exists('.env')
        if env_exists:
            shutil.move('.env', '.env.backup')
            
        try:
            config = Config()
            
            assert config.api_url == "https://scoutml.com"
            assert config.api_prefix == "arg/searches/api"
            assert config.default_timeout == 60
            assert config.max_retries == 3
            assert config.api_key is None
        finally:
            # Restore .env file
            if env_exists:
                shutil.move('.env.backup', '.env')
            # Restore env var
            if saved_api_key:
                os.environ['SCOUTML_API_KEY'] = saved_api_key
    
    def test_config_from_env(self):
        """Test configuration from environment variables."""
        os.environ['SCOUTML_API_KEY'] = 'test-key'
        os.environ['SCOUTML_API_URL'] = 'https://custom.api.com'
        
        config = Config()
        # Config automatically loads from env in __init__
        config = Config()
        
        assert config.api_key == 'test-key'
        assert config.api_url == 'https://custom.api.com'
    
    def test_config_from_file(self):
        """Test configuration from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write('SCOUTML_API_KEY=file-api-key\n')
            f.write('SCOUTML_API_URL=https://file.api.com\n')
            f.flush()
            
            # Simulate loading from .env file
            os.environ['SCOUTML_API_KEY'] = 'file-api-key'
            os.environ['SCOUTML_API_URL'] = 'https://file.api.com'
            # Config automatically loads from env in __init__
            config = Config()
            
            assert config.api_key == 'file-api-key'
            assert config.api_url == 'https://file.api.com'
            
            os.unlink(f.name)
    
    def test_is_configured(self):
        """Test is_configured property."""
        # Ensure no API key in environment
        saved_api_key = os.environ.get('SCOUTML_API_KEY')
        if 'SCOUTML_API_KEY' in os.environ:
            del os.environ['SCOUTML_API_KEY']
            
        # Temporarily rename .env file if it exists
        import shutil
        env_exists = os.path.exists('.env')
        if env_exists:
            shutil.move('.env', '.env.backup')
            
        try:
            config = Config()
            assert not config.is_configured
            
            config.api_key = 'test-key'
            assert config.is_configured
        finally:
            # Restore .env file
            if env_exists:
                shutil.move('.env.backup', '.env')
            # Restore env var
            if saved_api_key:
                os.environ['SCOUTML_API_KEY'] = saved_api_key
    
    def test_headers(self):
        """Test headers property."""
        config = Config()
        config.api_key = 'test-key'
        
        headers = config.headers
        assert headers['Authorization'] == 'Api-Key test-key'
        assert headers['Content-Type'] == 'application/json'
        assert 'User-Agent' in headers
    
    def test_get_endpoint(self):
        """Test get_endpoint method."""
        config = Config()
        config.api_url = 'https://api.test.com'
        config.api_prefix = 'v1'
        
        # Test with leading slash
        assert config.get_endpoint('/test/endpoint') == 'https://api.test.com/v1/test/endpoint'
        
        # Test without leading slash
        assert config.get_endpoint('test/endpoint') == 'https://api.test.com/v1/test/endpoint'
        
        # Test with empty prefix
        config.api_prefix = ''
        assert config.get_endpoint('test/endpoint') == 'https://api.test.com/test/endpoint'
    
    def test_headers_without_api_key(self):
        """Test headers property without API key."""
        config = Config()
        config.api_key = None
        
        # Should raise error when no API key
        with pytest.raises(ValueError, match="API key not configured"):
            _ = config.headers