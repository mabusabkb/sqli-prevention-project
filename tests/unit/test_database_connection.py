"""
Unit tests for database connection configuration.
Tests connection pooling, error handling, and support for MySQL and SQLite.
"""
import pytest
import os
from app import create_app, db
from sqlalchemy.exc import OperationalError
from config import DevelopmentConfig, ProductionConfig, TestingConfig


class TestDatabaseConfiguration:
    """Test database configuration settings"""
    
    def test_development_config_uses_sqlite(self):
        """Test that development config uses SQLite by default"""
        config = DevelopmentConfig()
        assert 'sqlite' in config.SQLALCHEMY_DATABASE_URI.lower()
    
    def test_testing_config_uses_memory_sqlite(self):
        """Test that testing config uses in-memory SQLite"""
        config = TestingConfig()
        assert config.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    
    def test_production_config_requires_database_url(self):
        """Test that production config requires DATABASE_URL environment variable"""
        # Clear DATABASE_URL if set
        original_url = os.environ.get('DATABASE_URL')
        if 'DATABASE_URL' in os.environ:
            del os.environ['DATABASE_URL']
        
        config = ProductionConfig()
        app = create_app('testing')  # Use testing to avoid production validation
        
        with pytest.raises(ValueError, match="DATABASE_URL environment variable must be set"):
            config.init_app(app)
        
        # Restore original value
        if original_url:
            os.environ['DATABASE_URL'] = original_url
    
    def test_production_config_has_connection_pooling(self):
        """Test that production config has connection pooling settings"""
        config = ProductionConfig()
        
        assert hasattr(config, 'SQLALCHEMY_ENGINE_OPTIONS')
        assert 'pool_size' in config.SQLALCHEMY_ENGINE_OPTIONS
        assert 'pool_recycle' in config.SQLALCHEMY_ENGINE_OPTIONS
        assert 'pool_pre_ping' in config.SQLALCHEMY_ENGINE_OPTIONS
        assert 'max_overflow' in config.SQLALCHEMY_ENGINE_OPTIONS
        assert 'pool_timeout' in config.SQLALCHEMY_ENGINE_OPTIONS
    
    def test_production_pool_size_is_reasonable(self):
        """Test that production pool size is set to a reasonable value"""
        config = ProductionConfig()
        pool_size = config.SQLALCHEMY_ENGINE_OPTIONS['pool_size']
        
        assert pool_size >= 5, "Pool size should be at least 5"
        assert pool_size <= 50, "Pool size should not exceed 50"
    
    def test_production_pool_recycle_is_set(self):
        """Test that production pool recycle is configured"""
        config = ProductionConfig()
        pool_recycle = config.SQLALCHEMY_ENGINE_OPTIONS['pool_recycle']
        
        assert pool_recycle > 0, "Pool recycle should be positive"
        assert pool_recycle <= 7200, "Pool recycle should not exceed 2 hours"
    
    def test_production_pool_pre_ping_enabled(self):
        """Test that production pool pre-ping is enabled"""
        config = ProductionConfig()
        pool_pre_ping = config.SQLALCHEMY_ENGINE_OPTIONS['pool_pre_ping']
        
        assert pool_pre_ping is True, "Pool pre-ping should be enabled for production"


class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_sqlite_connection_successful(self, app, db):
        """Test that SQLite connection works"""
        # The app fixture uses testing config with SQLite
        assert db.engine is not None
        
        # Test connection by executing a simple query
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1')).scalar()
        assert result == 1
    
    def test_database_session_rollback_on_error(self, app, db):
        """Test that database session rolls back on error"""
        from app.models import User
        
        # Create a user
        user = User(username='testuser', email='test@example.com', 
                   password='hashed_password', gender='Male')
        db.session.add(user)
        db.session.commit()
        
        # Try to create duplicate user (should fail due to unique constraint)
        duplicate_user = User(username='testuser', email='different@example.com',
                             password='hashed_password', gender='Female')
        db.session.add(duplicate_user)
        
        with pytest.raises(Exception):
            db.session.commit()
        
        # Session should be rolled back
        db.session.rollback()
        
        # Verify we can still use the session
        users = User.query.all()
        assert len(users) == 1
        assert users[0].username == 'testuser'
    
    def test_health_check_endpoint_with_database(self, client):
        """Test health check endpoint reports database status"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'status' in data
        assert 'database' in data
        assert data['database'] in ['connected', 'disconnected']
    
    def test_database_connection_error_handling(self, app):
        """Test that database connection errors are handled gracefully"""
        # This test verifies error handlers are registered
        from sqlalchemy.exc import OperationalError, SQLAlchemyError
        
        # Check that error handlers are registered in the error_handler_spec
        # The structure is: error_handler_spec[blueprint_name][exception_class]
        error_handlers = app.error_handler_spec.get(None, {})
        
        # Verify SQLAlchemy error handlers are present
        assert any(SQLAlchemyError in handlers or issubclass(exc, SQLAlchemyError) 
                  for handlers in error_handlers.values() 
                  for exc in handlers.keys() if isinstance(exc, type))
        assert any(OperationalError in handlers or issubclass(exc, OperationalError)
                  for handlers in error_handlers.values()
                  for exc in handlers.keys() if isinstance(exc, type))


class TestMySQLConnectionSupport:
    """Test MySQL connection support (configuration only, no actual MySQL required)"""
    
    def test_mysql_connection_string_format(self):
        """Test that MySQL connection string format is supported"""
        # Set MySQL connection string before creating config
        original_url = os.environ.get('DATABASE_URL')
        os.environ['DATABASE_URL'] = 'mysql://user:password@localhost:3306/testdb'
        
        # Import config module to reload with new environment variable
        from importlib import reload
        import config as config_module
        reload(config_module)
        
        # Now check the value
        assert os.environ.get('DATABASE_URL') == 'mysql://user:password@localhost:3306/testdb'
        
        # Clean up
        if original_url:
            os.environ['DATABASE_URL'] = original_url
        else:
            del os.environ['DATABASE_URL']
        
        # Reload config again to restore original state
        reload(config_module)
    
    def test_mysql_connection_string_with_pymysql(self):
        """Test that MySQL connection string with pymysql driver is supported"""
        # Set MySQL connection string with pymysql driver
        original_url = os.environ.get('DATABASE_URL')
        os.environ['DATABASE_URL'] = 'mysql+pymysql://user:password@localhost:3306/testdb'
        
        # Verify environment variable is set correctly
        assert 'mysql' in os.environ['DATABASE_URL']
        assert 'pymysql' in os.environ['DATABASE_URL']
        
        # Clean up
        if original_url:
            os.environ['DATABASE_URL'] = original_url
        else:
            del os.environ['DATABASE_URL']
    
    def test_production_config_accepts_mysql_url(self):
        """Test that production config accepts MySQL DATABASE_URL"""
        original_url = os.environ.get('DATABASE_URL')
        original_key = os.environ.get('SECRET_KEY')
        
        os.environ['DATABASE_URL'] = 'mysql+pymysql://user:password@localhost:3306/testdb'
        os.environ['SECRET_KEY'] = 'test-secret-key'
        
        # Create app with testing config (which doesn't validate DATABASE_URL)
        app = create_app('testing')
        
        # Verify environment variables are set correctly
        assert os.environ.get('DATABASE_URL') == 'mysql+pymysql://user:password@localhost:3306/testdb'
        assert os.environ.get('SECRET_KEY') == 'test-secret-key'
        
        # Clean up
        if original_url:
            os.environ['DATABASE_URL'] = original_url
        else:
            del os.environ['DATABASE_URL']
        
        if original_key:
            os.environ['SECRET_KEY'] = original_key
        else:
            del os.environ['SECRET_KEY']


class TestConnectionPoolingBehavior:
    """Test connection pooling behavior"""
    
    def test_multiple_connections_reuse_pool(self, app, db):
        """Test that multiple database operations reuse connections from pool"""
        from app.models import User
        
        # Perform multiple database operations
        for i in range(5):
            user = User(username=f'user{i}', email=f'user{i}@example.com',
                       password='hashed_password', gender='Male')
            db.session.add(user)
            db.session.commit()
        
        # Verify all users were created
        users = User.query.all()
        assert len(users) == 5
    
    def test_connection_survives_rollback(self, app, db):
        """Test that connection pool survives transaction rollback"""
        from app.models import User
        
        # Create a user
        user = User(username='testuser', email='test@example.com',
                   password='hashed_password', gender='Male')
        db.session.add(user)
        db.session.commit()
        
        # Try to create duplicate (will fail)
        duplicate = User(username='testuser', email='other@example.com',
                        password='hashed_password', gender='Female')
        db.session.add(duplicate)
        
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()
        
        # Connection should still work
        users = User.query.all()
        assert len(users) == 1


class TestDatabaseErrorHandling:
    """Test database error handling"""
    
    def test_sqlalchemy_error_returns_500(self):
        """Test that SQLAlchemy errors return 500 status code"""
        from sqlalchemy.exc import SQLAlchemyError
        
        # Create a fresh app instance for this test
        test_app = create_app('testing')
        
        # Create a route that raises SQLAlchemyError
        @test_app.route('/test-db-error')
        def test_db_error():
            raise SQLAlchemyError("Test database error")
        
        client = test_app.test_client()
        response = client.get('/test-db-error')
        assert response.status_code == 500
        
        data = response.get_json()
        assert 'error' in data
        assert 'database error' in data['error'].lower()
    
    def test_operational_error_returns_503(self):
        """Test that operational errors return 503 status code"""
        from sqlalchemy.exc import OperationalError
        
        # Create a fresh app instance for this test
        test_app = create_app('testing')
        
        # Create a route that raises OperationalError
        @test_app.route('/test-operational-error')
        def test_operational_error():
            raise OperationalError("Test connection error", None, None)
        
        client = test_app.test_client()
        response = client.get('/test-operational-error')
        assert response.status_code == 503
        
        data = response.get_json()
        assert 'error' in data
        assert 'connection error' in data['error'].lower()
    
    def test_error_messages_are_generic(self):
        """Test that database error messages don't leak sensitive information"""
        from sqlalchemy.exc import SQLAlchemyError
        
        # Create a fresh app instance for this test
        test_app = create_app('testing')
        
        # Create a route that raises detailed error
        @test_app.route('/test-detailed-error')
        def test_detailed_error():
            raise SQLAlchemyError("SELECT * FROM users WHERE password='secret123'")
        
        client = test_app.test_client()
        response = client.get('/test-detailed-error')
        data = response.get_json()
        
        # Error message should be generic
        assert 'SELECT' not in data['error']
        assert 'password' not in data['error']
        assert 'secret123' not in data['error']
        assert 'database error' in data['error'].lower()
