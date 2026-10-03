"""
Configuration parser and validator.
Validates configuration dictionaries and converts them to Configuration objects.
"""
import re
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass


@dataclass
class Configuration:
    """Configuration object representing validated application configuration"""
    secret_key: str
    database_url: str
    flask_env: str
    log_level: str
    bcrypt_rounds: int
    session_timeout_hours: int
    
    def __eq__(self, other):
        """Equality comparison for round-trip testing"""
        if not isinstance(other, Configuration):
            return False
        return (
            self.secret_key == other.secret_key and
            self.database_url == other.database_url and
            self.flask_env == other.flask_env and
            self.log_level == other.log_level and
            self.bcrypt_rounds == other.bcrypt_rounds and
            self.session_timeout_hours == other.session_timeout_hours
        )


class ConfigurationParser:
    """Parses and validates configuration dictionaries"""
    
    REQUIRED_KEYS = ['SECRET_KEY', 'DATABASE_URL', 'FLASK_ENV']
    VALID_FLASK_ENVS = ['development', 'testing', 'production']
    VALID_LOG_LEVELS = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    MIN_BCRYPT_ROUNDS = 10
    MAX_BCRYPT_ROUNDS = 20
    
    @staticmethod
    def parse(config_dict: Dict[str, Any]) -> Tuple[bool, Optional[Configuration], Optional[str]]:
        """
        Parse configuration dictionary into Configuration object.
        
        Validates:
        - Required keys are present
        - FLASK_ENV is one of: development, testing, production
        - LOG_LEVEL is one of: DEBUG, INFO, WARNING, ERROR, CRITICAL
        - BCRYPT_LOG_ROUNDS is an integer between 10 and 20
        - DATABASE_URL has valid format (dialect://...)
        
        Args:
            config_dict: Dictionary containing configuration key-value pairs
            
        Returns:
            Tuple of (success, configuration_object, error_message)
            - success: True if parsing succeeded, False otherwise
            - configuration_object: Configuration instance if success, None otherwise
            - error_message: Descriptive error message if failed, None otherwise
        """
        # Check required keys
        missing_keys = [key for key in ConfigurationParser.REQUIRED_KEYS if key not in config_dict]
        if missing_keys:
            return False, None, f"Missing required configuration keys: {', '.join(missing_keys)}"
        
        # Validate FLASK_ENV
        flask_env = config_dict.get('FLASK_ENV')
        if flask_env not in ConfigurationParser.VALID_FLASK_ENVS:
            return False, None, f"Invalid FLASK_ENV. Must be one of: {', '.join(ConfigurationParser.VALID_FLASK_ENVS)}"
        
        # Validate LOG_LEVEL (optional, defaults to INFO)
        log_level = config_dict.get('LOG_LEVEL', 'INFO')
        if log_level not in ConfigurationParser.VALID_LOG_LEVELS:
            return False, None, f"Invalid LOG_LEVEL. Must be one of: {', '.join(ConfigurationParser.VALID_LOG_LEVELS)}"
        
        # Validate BCRYPT_LOG_ROUNDS (optional, defaults to 12)
        try:
            bcrypt_rounds = int(config_dict.get('BCRYPT_LOG_ROUNDS', 12))
            if bcrypt_rounds < ConfigurationParser.MIN_BCRYPT_ROUNDS or bcrypt_rounds > ConfigurationParser.MAX_BCRYPT_ROUNDS:
                return False, None, f"BCRYPT_LOG_ROUNDS must be between {ConfigurationParser.MIN_BCRYPT_ROUNDS} and {ConfigurationParser.MAX_BCRYPT_ROUNDS}"
        except (ValueError, TypeError):
            return False, None, "BCRYPT_LOG_ROUNDS must be an integer"
        
        # Validate SESSION_TIMEOUT_HOURS (optional, defaults to 1)
        try:
            session_timeout = int(config_dict.get('SESSION_TIMEOUT_HOURS', 1))
            if session_timeout < 1:
                return False, None, "SESSION_TIMEOUT_HOURS must be at least 1"
        except (ValueError, TypeError):
            return False, None, "SESSION_TIMEOUT_HOURS must be an integer"
        
        # Validate DATABASE_URL format
        database_url = config_dict.get('DATABASE_URL')
        if not ConfigurationParser._validate_database_url(database_url):
            return False, None, "Invalid DATABASE_URL format"
        
        # Create Configuration object
        config = Configuration(
            secret_key=config_dict['SECRET_KEY'],
            database_url=database_url,
            flask_env=flask_env,
            log_level=log_level,
            bcrypt_rounds=bcrypt_rounds,
            session_timeout_hours=session_timeout
        )
        
        return True, config, None
    
    @staticmethod
    def _validate_database_url(url: str) -> bool:
        """
        Validate database URL format.
        
        Accepts URLs in the format: dialect://...
        Examples:
        - sqlite:///path/to/db.db
        - mysql://user:pass@host:port/dbname
        - postgresql+psycopg2://user:pass@host/dbname
        
        Args:
            url: Database URL string to validate
            
        Returns:
            True if URL format is valid, False otherwise
        """
        if not url:
            return False
        
        # Basic format check: dialect://... or dialect+driver://...
        pattern = r'^[a-z]+(\+[a-z0-9]+)?://.+'
        return bool(re.match(pattern, url))
    
    @staticmethod
    def format(config: Configuration) -> Dict[str, Any]:
        """
        Format Configuration object back into dictionary.
        
        This enables round-trip conversion: dict -> Configuration -> dict
        
        Args:
            config: Configuration object to convert
            
        Returns:
            Dictionary with configuration key-value pairs
        """
        return {
            'SECRET_KEY': config.secret_key,
            'DATABASE_URL': config.database_url,
            'FLASK_ENV': config.flask_env,
            'LOG_LEVEL': config.log_level,
            'BCRYPT_LOG_ROUNDS': config.bcrypt_rounds,
            'SESSION_TIMEOUT_HOURS': config.session_timeout_hours
        }
