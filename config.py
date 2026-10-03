"""
Configuration classes for Flask application.
Supports development, testing, and production environments.
"""
import os
from datetime import timedelta


class Config:
    """Base configuration with common settings"""
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # SQLAlchemy settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(hours=1)
    
    # Bcrypt configuration
    BCRYPT_LOG_ROUNDS = 12


class DevelopmentConfig(Config):
    """Development environment configuration"""
    
    DEBUG = True
    TESTING = False
    
    # Use SQLite for development by default
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///dev.db'
    
    # Development doesn't require HTTPS
    SESSION_COOKIE_SECURE = False
    
    # Log SQL queries in development
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    """Testing environment configuration"""
    
    DEBUG = False
    TESTING = True
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Faster bcrypt for tests
    BCRYPT_LOG_ROUNDS = 4
    
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production environment configuration"""
    
    DEBUG = False
    TESTING = False
    
    # Require DATABASE_URL in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    
    # Connection pooling settings for production
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,           # Maximum number of connections to keep open
        'pool_recycle': 3600,      # Recycle connections after 1 hour
        'pool_pre_ping': True,     # Verify connections before using them
        'max_overflow': 20,        # Maximum number of connections to create beyond pool_size
        'pool_timeout': 30,        # Timeout for getting a connection from the pool
    }
    
    # Production requires HTTPS
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'
    
    @classmethod
    def init_app(cls, app):
        """Validate production configuration"""
        if not cls.SQLALCHEMY_DATABASE_URI:
            raise ValueError("DATABASE_URL environment variable must be set in production")
        
        if not os.environ.get('SECRET_KEY'):
            raise ValueError("SECRET_KEY environment variable must be set in production")


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
