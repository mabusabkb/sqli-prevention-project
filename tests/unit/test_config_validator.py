"""
Unit tests for ConfigurationParser.
Tests validation of configuration dictionaries and conversion to Configuration objects.
"""
import pytest
from app.validators import Configuration, ConfigurationParser


class TestConfigurationParser:
    """Test suite for ConfigurationParser"""
    
    def test_parse_valid_configuration(self):
        """Test parsing a valid configuration dictionary"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development',
            'LOG_LEVEL': 'DEBUG',
            'BCRYPT_LOG_ROUNDS': 12,
            'SESSION_TIMEOUT_HOURS': 2
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is True
        assert error is None
        assert config is not None
        assert config.secret_key == 'test-secret-key'
        assert config.database_url == 'sqlite:///test.db'
        assert config.flask_env == 'development'
        assert config.log_level == 'DEBUG'
        assert config.bcrypt_rounds == 12
        assert config.session_timeout_hours == 2
    
    def test_parse_with_defaults(self):
        """Test parsing with optional fields using defaults"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'production'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is True
        assert error is None
        assert config.log_level == 'INFO'  # Default
        assert config.bcrypt_rounds == 12  # Default
        assert config.session_timeout_hours == 1  # Default
    
    def test_parse_missing_secret_key(self):
        """Test parsing fails when SECRET_KEY is missing"""
        config_dict = {
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'SECRET_KEY' in error
        assert 'Missing required configuration keys' in error
    
    def test_parse_missing_database_url(self):
        """Test parsing fails when DATABASE_URL is missing"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'FLASK_ENV': 'development'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'DATABASE_URL' in error
        assert 'Missing required configuration keys' in error
    
    def test_parse_missing_flask_env(self):
        """Test parsing fails when FLASK_ENV is missing"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'FLASK_ENV' in error
        assert 'Missing required configuration keys' in error
    
    def test_parse_invalid_flask_env(self):
        """Test parsing fails with invalid FLASK_ENV value"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'invalid_env'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'Invalid FLASK_ENV' in error
        assert 'development' in error
        assert 'testing' in error
        assert 'production' in error
    
    def test_parse_valid_flask_env_development(self):
        """Test parsing succeeds with FLASK_ENV=development"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is True
        assert config.flask_env == 'development'
    
    def test_parse_valid_flask_env_testing(self):
        """Test parsing succeeds with FLASK_ENV=testing"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'testing'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is True
        assert config.flask_env == 'testing'
    
    def test_parse_valid_flask_env_production(self):
        """Test parsing succeeds with FLASK_ENV=production"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'production'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is True
        assert config.flask_env == 'production'
    
    def test_parse_invalid_log_level(self):
        """Test parsing fails with invalid LOG_LEVEL value"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development',
            'LOG_LEVEL': 'INVALID'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'Invalid LOG_LEVEL' in error
        assert 'DEBUG' in error
        assert 'INFO' in error
        assert 'WARNING' in error
        assert 'ERROR' in error
        assert 'CRITICAL' in error
    
    def test_parse_valid_log_levels(self):
        """Test parsing succeeds with all valid LOG_LEVEL values"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in valid_levels:
            config_dict = {
                'SECRET_KEY': 'test-secret-key',
                'DATABASE_URL': 'sqlite:///test.db',
                'FLASK_ENV': 'development',
                'LOG_LEVEL': level
            }
            
            success, config, error = ConfigurationParser.parse(config_dict)
            
            assert success is True, f"Failed for LOG_LEVEL={level}"
            assert config.log_level == level
    
    def test_parse_bcrypt_rounds_below_minimum(self):
        """Test parsing fails when BCRYPT_LOG_ROUNDS is below 10"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development',
            'BCRYPT_LOG_ROUNDS': 9
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'BCRYPT_LOG_ROUNDS must be between 10 and 20' in error
    
    def test_parse_bcrypt_rounds_above_maximum(self):
        """Test parsing fails when BCRYPT_LOG_ROUNDS is above 20"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development',
            'BCRYPT_LOG_ROUNDS': 21
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'BCRYPT_LOG_ROUNDS must be between 10 and 20' in error
    
    def test_parse_bcrypt_rounds_valid_range(self):
        """Test parsing succeeds with BCRYPT_LOG_ROUNDS in valid range (10-20)"""
        for rounds in [10, 12, 15, 20]:
            config_dict = {
                'SECRET_KEY': 'test-secret-key',
                'DATABASE_URL': 'sqlite:///test.db',
                'FLASK_ENV': 'development',
                'BCRYPT_LOG_ROUNDS': rounds
            }
            
            success, config, error = ConfigurationParser.parse(config_dict)
            
            assert success is True, f"Failed for BCRYPT_LOG_ROUNDS={rounds}"
            assert config.bcrypt_rounds == rounds
    
    def test_parse_bcrypt_rounds_invalid_type(self):
        """Test parsing fails when BCRYPT_LOG_ROUNDS is not an integer"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development',
            'BCRYPT_LOG_ROUNDS': 'not_an_integer'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'BCRYPT_LOG_ROUNDS must be an integer' in error
    
    def test_parse_session_timeout_invalid_type(self):
        """Test parsing fails when SESSION_TIMEOUT_HOURS is not an integer"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development',
            'SESSION_TIMEOUT_HOURS': 'not_an_integer'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'SESSION_TIMEOUT_HOURS must be an integer' in error
    
    def test_parse_session_timeout_below_minimum(self):
        """Test parsing fails when SESSION_TIMEOUT_HOURS is less than 1"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'development',
            'SESSION_TIMEOUT_HOURS': 0
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'SESSION_TIMEOUT_HOURS must be at least 1' in error
    
    def test_parse_invalid_database_url_empty(self):
        """Test parsing fails with empty DATABASE_URL"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': '',
            'FLASK_ENV': 'development'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'Invalid DATABASE_URL format' in error
    
    def test_parse_invalid_database_url_no_protocol(self):
        """Test parsing fails with DATABASE_URL missing protocol"""
        config_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'just_a_path.db',
            'FLASK_ENV': 'development'
        }
        
        success, config, error = ConfigurationParser.parse(config_dict)
        
        assert success is False
        assert config is None
        assert 'Invalid DATABASE_URL format' in error
    
    def test_parse_valid_database_url_sqlite(self):
        """Test parsing succeeds with valid SQLite DATABASE_URL"""
        urls = [
            'sqlite:///test.db',
            'sqlite:////absolute/path/test.db',
            'sqlite:///:memory:'
        ]
        
        for url in urls:
            config_dict = {
                'SECRET_KEY': 'test-secret-key',
                'DATABASE_URL': url,
                'FLASK_ENV': 'development'
            }
            
            success, config, error = ConfigurationParser.parse(config_dict)
            
            assert success is True, f"Failed for DATABASE_URL={url}"
            assert config.database_url == url
    
    def test_parse_valid_database_url_mysql(self):
        """Test parsing succeeds with valid MySQL DATABASE_URL"""
        urls = [
            'mysql://user:pass@localhost/dbname',
            'mysql+pymysql://user:pass@localhost:3306/dbname'
        ]
        
        for url in urls:
            config_dict = {
                'SECRET_KEY': 'test-secret-key',
                'DATABASE_URL': url,
                'FLASK_ENV': 'development'
            }
            
            success, config, error = ConfigurationParser.parse(config_dict)
            
            assert success is True, f"Failed for DATABASE_URL={url}"
            assert config.database_url == url
    
    def test_parse_valid_database_url_postgresql(self):
        """Test parsing succeeds with valid PostgreSQL DATABASE_URL"""
        urls = [
            'postgresql://user:pass@localhost/dbname',
            'postgresql+psycopg2://user:pass@localhost:5432/dbname'
        ]
        
        for url in urls:
            config_dict = {
                'SECRET_KEY': 'test-secret-key',
                'DATABASE_URL': url,
                'FLASK_ENV': 'development'
            }
            
            success, config, error = ConfigurationParser.parse(config_dict)
            
            assert success is True, f"Failed for DATABASE_URL={url}"
            assert config.database_url == url
    
    def test_format_configuration(self):
        """Test formatting Configuration object back to dictionary"""
        config = Configuration(
            secret_key='test-secret-key',
            database_url='sqlite:///test.db',
            flask_env='development',
            log_level='DEBUG',
            bcrypt_rounds=12,
            session_timeout_hours=2
        )
        
        config_dict = ConfigurationParser.format(config)
        
        assert config_dict['SECRET_KEY'] == 'test-secret-key'
        assert config_dict['DATABASE_URL'] == 'sqlite:///test.db'
        assert config_dict['FLASK_ENV'] == 'development'
        assert config_dict['LOG_LEVEL'] == 'DEBUG'
        assert config_dict['BCRYPT_LOG_ROUNDS'] == 12
        assert config_dict['SESSION_TIMEOUT_HOURS'] == 2
    
    def test_configuration_equality(self):
        """Test Configuration equality comparison"""
        config1 = Configuration(
            secret_key='test-secret-key',
            database_url='sqlite:///test.db',
            flask_env='development',
            log_level='DEBUG',
            bcrypt_rounds=12,
            session_timeout_hours=2
        )
        
        config2 = Configuration(
            secret_key='test-secret-key',
            database_url='sqlite:///test.db',
            flask_env='development',
            log_level='DEBUG',
            bcrypt_rounds=12,
            session_timeout_hours=2
        )
        
        assert config1 == config2
    
    def test_configuration_inequality(self):
        """Test Configuration inequality when values differ"""
        config1 = Configuration(
            secret_key='test-secret-key',
            database_url='sqlite:///test.db',
            flask_env='development',
            log_level='DEBUG',
            bcrypt_rounds=12,
            session_timeout_hours=2
        )
        
        config2 = Configuration(
            secret_key='different-secret-key',
            database_url='sqlite:///test.db',
            flask_env='development',
            log_level='DEBUG',
            bcrypt_rounds=12,
            session_timeout_hours=2
        )
        
        assert config1 != config2
    
    def test_round_trip_conversion(self):
        """Test that parse -> format -> parse preserves all values"""
        original_dict = {
            'SECRET_KEY': 'test-secret-key',
            'DATABASE_URL': 'sqlite:///test.db',
            'FLASK_ENV': 'production',
            'LOG_LEVEL': 'WARNING',
            'BCRYPT_LOG_ROUNDS': 15,
            'SESSION_TIMEOUT_HOURS': 3
        }
        
        # Parse to Configuration
        success1, config, error1 = ConfigurationParser.parse(original_dict)
        assert success1 is True
        
        # Format back to dict
        formatted_dict = ConfigurationParser.format(config)
        
        # Parse again
        success2, config2, error2 = ConfigurationParser.parse(formatted_dict)
        assert success2 is True
        
        # Verify configurations are equal
        assert config == config2
