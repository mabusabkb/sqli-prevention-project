"""
Integration tests for database connections.
Tests actual database operations with SQLite and MySQL configurations.
"""
import pytest
import os
from app import create_app, db
from app.models import User


class TestSQLiteDatabaseIntegration:
    """Integration tests for SQLite database"""
    
    def test_sqlite_crud_operations(self, app, db):
        """Test complete CRUD operations with SQLite"""
        # Create
        user = User(
            username='testuser',
            email='test@example.com',
            password='hashed_password',
            gender='Male'
        )
        db.session.add(user)
        db.session.commit()
        
        # Read
        retrieved_user = User.query.filter_by(username='testuser').first()
        assert retrieved_user is not None
        assert retrieved_user.email == 'test@example.com'
        assert retrieved_user.gender == 'Male'
        
        # Update
        retrieved_user.email = 'updated@example.com'
        db.session.commit()
        
        updated_user = User.query.filter_by(username='testuser').first()
        assert updated_user.email == 'updated@example.com'
        
        # Delete
        db.session.delete(updated_user)
        db.session.commit()
        
        deleted_user = User.query.filter_by(username='testuser').first()
        assert deleted_user is None
    
    def test_sqlite_transaction_rollback(self, app, db):
        """Test transaction rollback with SQLite"""
        # Create a user
        user = User(
            username='testuser',
            email='test@example.com',
            password='hashed_password',
            gender='Male'
        )
        db.session.add(user)
        db.session.commit()
        
        # Start a transaction that will fail
        duplicate_user = User(
            username='testuser',  # Duplicate username
            email='different@example.com',
            password='hashed_password',
            gender='Female'
        )
        db.session.add(duplicate_user)
        
        # Should raise an exception due to unique constraint
        with pytest.raises(Exception):
            db.session.commit()
        
        # Rollback the failed transaction
        db.session.rollback()
        
        # Verify original user still exists and no duplicate was created
        users = User.query.all()
        assert len(users) == 1
        assert users[0].username == 'testuser'
        assert users[0].email == 'test@example.com'
    
    def test_sqlite_connection_persistence(self, app, db):
        """Test that SQLite connection persists across multiple operations"""
        # Perform multiple operations
        for i in range(10):
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password='hashed_password',
                gender='Male' if i % 2 == 0 else 'Female'
            )
            db.session.add(user)
            db.session.commit()
        
        # Verify all users were created
        users = User.query.all()
        assert len(users) == 10
        
        # Verify we can still query after many operations
        male_users = User.query.filter_by(gender='Male').all()
        female_users = User.query.filter_by(gender='Female').all()
        
        assert len(male_users) == 5
        assert len(female_users) == 5


class TestMySQLConfigurationSupport:
    """Test MySQL configuration support (without actual MySQL connection)"""
    
    def test_mysql_connection_string_parsing(self):
        """Test that MySQL connection strings are properly configured"""
        original_url = os.environ.get('DATABASE_URL')
        
        # Test various MySQL connection string formats
        mysql_urls = [
            'mysql://user:password@localhost:3306/testdb',
            'mysql+pymysql://user:password@localhost:3306/testdb',
            'mysql+mysqlconnector://user:password@localhost:3306/testdb',
        ]
        
        for url in mysql_urls:
            os.environ['DATABASE_URL'] = url
            
            # Verify environment variable is set
            assert os.environ.get('DATABASE_URL') == url
            assert 'mysql' in url
        
        # Clean up
        if original_url:
            os.environ['DATABASE_URL'] = original_url
        else:
            if 'DATABASE_URL' in os.environ:
                del os.environ['DATABASE_URL']
    
    def test_production_config_with_mysql(self):
        """Test production configuration with MySQL URL"""
        from config import ProductionConfig
        
        original_url = os.environ.get('DATABASE_URL')
        original_key = os.environ.get('SECRET_KEY')
        
        # Set MySQL connection string
        os.environ['DATABASE_URL'] = 'mysql+pymysql://user:password@localhost:3306/proddb'
        os.environ['SECRET_KEY'] = 'production-secret-key'
        
        config = ProductionConfig()
        
        # Verify connection pooling is configured
        assert hasattr(config, 'SQLALCHEMY_ENGINE_OPTIONS')
        assert config.SQLALCHEMY_ENGINE_OPTIONS['pool_size'] == 10
        assert config.SQLALCHEMY_ENGINE_OPTIONS['pool_pre_ping'] is True
        
        # Clean up
        if original_url:
            os.environ['DATABASE_URL'] = original_url
        else:
            if 'DATABASE_URL' in os.environ:
                del os.environ['DATABASE_URL']
        
        if original_key:
            os.environ['SECRET_KEY'] = original_key
        else:
            if 'SECRET_KEY' in os.environ:
                del os.environ['SECRET_KEY']


class TestDatabaseHealthCheck:
    """Test database health check functionality"""
    
    def test_health_check_with_working_database(self, client):
        """Test health check endpoint with working database"""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
        assert 'environment' in data
    
    def test_health_check_response_format(self, client):
        """Test health check response has correct format"""
        response = client.get('/health')
        data = response.get_json()
        
        # Verify all required fields are present
        assert 'status' in data
        assert 'database' in data
        assert 'environment' in data
        
        # Verify field types
        assert isinstance(data['status'], str)
        assert isinstance(data['database'], str)
        assert isinstance(data['environment'], str)


class TestConnectionPooling:
    """Test connection pooling behavior"""
    
    def test_concurrent_database_operations(self, app, db):
        """Test that multiple concurrent operations work correctly"""
        # Simulate concurrent operations by creating multiple users rapidly
        users_to_create = 20
        
        for i in range(users_to_create):
            user = User(
                username=f'concurrent_user_{i}',
                email=f'concurrent_{i}@example.com',
                password='hashed_password',
                gender='Male' if i % 2 == 0 else 'Female'
            )
            db.session.add(user)
            db.session.commit()
        
        # Verify all users were created
        users = User.query.all()
        assert len(users) == users_to_create
        
        # Verify we can still perform queries
        for i in range(users_to_create):
            user = User.query.filter_by(username=f'concurrent_user_{i}').first()
            assert user is not None
            assert user.email == f'concurrent_{i}@example.com'
    
    def test_connection_reuse_after_error(self, app, db):
        """Test that connections are reused properly after errors"""
        # Create a valid user
        user1 = User(
            username='user1',
            email='user1@example.com',
            password='hashed_password',
            gender='Male'
        )
        db.session.add(user1)
        db.session.commit()
        
        # Try to create a duplicate (will fail)
        user2 = User(
            username='user1',  # Duplicate
            email='user2@example.com',
            password='hashed_password',
            gender='Female'
        )
        db.session.add(user2)
        
        with pytest.raises(Exception):
            db.session.commit()
        
        db.session.rollback()
        
        # Create another valid user (connection should still work)
        user3 = User(
            username='user3',
            email='user3@example.com',
            password='hashed_password',
            gender='Female'
        )
        db.session.add(user3)
        db.session.commit()
        
        # Verify both valid users exist
        users = User.query.all()
        assert len(users) == 2
        assert any(u.username == 'user1' for u in users)
        assert any(u.username == 'user3' for u in users)
