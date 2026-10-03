"""
Unit tests for AuthService.
Tests user registration and authentication functionality.
"""
import pytest
from app.services.auth_service import AuthService
from app.models.user import User
from app import bcrypt


class TestAuthServiceRegistration:
    """Test cases for user registration"""
    
    def test_register_user_success(self, app, db):
        """Test successful user registration"""
        # Register new user
        success, error = AuthService.register_user(
            username="testuser",
            email="test@example.com",
            password="testpassword123",
            gender="Male"
        )
        
        # Assert registration succeeded
        assert success is True
        assert error is None
        
        # Verify user was created in database
        user = User.query.filter_by(username="testuser").first()
        assert user is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.gender == "Male"
        
        # Verify password was hashed (not stored as plain text)
        assert user.password != "testpassword123"
        assert user.password.startswith('$2b$')  # Bcrypt hash format
        
        # Verify password can be verified
        assert bcrypt.check_password_hash(user.password, "testpassword123")
    
    def test_register_user_duplicate_username(self, app, db):
        """Test registration with duplicate username fails"""
        # Register first user
        success1, error1 = AuthService.register_user(
            username="testuser",
            email="test1@example.com",
            password="password123",
            gender="Male"
        )
        assert success1 is True
        
        # Try to register second user with same username
        success2, error2 = AuthService.register_user(
            username="testuser",
            email="test2@example.com",
            password="password456",
            gender="Female"
        )
        
        # Assert registration failed
        assert success2 is False
        assert error2 == "Username already exists"
        
        # Verify only one user exists
        users = User.query.filter_by(username="testuser").all()
        assert len(users) == 1
    
    def test_register_user_duplicate_email(self, app, db):
        """Test registration with duplicate email fails"""
        # Register first user
        success1, error1 = AuthService.register_user(
            username="user1",
            email="test@example.com",
            password="password123",
            gender="Male"
        )
        assert success1 is True
        
        # Try to register second user with same email
        success2, error2 = AuthService.register_user(
            username="user2",
            email="test@example.com",
            password="password456",
            gender="Female"
        )
        
        # Assert registration failed
        assert success2 is False
        assert error2 == "Email already registered"
        
        # Verify only one user exists with that email
        users = User.query.filter_by(email="test@example.com").all()
        assert len(users) == 1
    
    def test_register_user_bcrypt_cost_factor(self, app, db):
        """Test that password is hashed with bcrypt cost factor >= 12"""
        # Register user
        success, error = AuthService.register_user(
            username="testuser",
            email="test@example.com",
            password="testpassword",
            gender="Male"
        )
        assert success is True
        
        # Get user from database
        user = User.query.filter_by(username="testuser").first()
        
        # Extract cost factor from bcrypt hash
        # Bcrypt hash format: $2b$12$...
        # The cost factor is the number after the second $
        hash_parts = user.password.split('$')
        cost_factor = int(hash_parts[2])
        
        # Assert cost factor is at least 12
        assert cost_factor >= 12
    
    def test_register_user_password_not_plain_text(self, app, db):
        """Test that password is never stored as plain text"""
        password = "mysecretpassword"
        
        # Register user
        success, error = AuthService.register_user(
            username="testuser",
            email="test@example.com",
            password=password,
            gender="Female"
        )
        assert success is True
        
        # Get user from database
        user = User.query.filter_by(username="testuser").first()
        
        # Assert password is not stored as plain text
        assert user.password != password
        
        # Assert password is a bcrypt hash
        assert user.password.startswith('$2b$') or user.password.startswith('$2y$')
        assert len(user.password) == 60  # Bcrypt hashes are always 60 characters


class TestAuthServiceAuthentication:
    """Test cases for user authentication"""
    
    def test_authenticate_user_success(self, app, db):
        """Test successful authentication"""
        # Register user first
        AuthService.register_user(
            username="testuser",
            email="test@example.com",
            password="correctpassword",
            gender="Male"
        )
        
        # Authenticate with correct credentials
        success, user, error = AuthService.authenticate_user(
            username="testuser",
            password="correctpassword"
        )
        
        # Assert authentication succeeded
        assert success is True
        assert user is not None
        assert error is None
        assert user.username == "testuser"
    
    def test_authenticate_user_wrong_password(self, app, db):
        """Test authentication with wrong password fails"""
        # Register user first
        AuthService.register_user(
            username="testuser",
            email="test@example.com",
            password="correctpassword",
            gender="Male"
        )
        
        # Authenticate with wrong password
        success, user, error = AuthService.authenticate_user(
            username="testuser",
            password="wrongpassword"
        )
        
        # Assert authentication failed
        assert success is False
        assert user is None
        assert error == "Invalid username or password"
    
    def test_authenticate_user_nonexistent_username(self, app, db):
        """Test authentication with non-existent username fails"""
        # Try to authenticate with non-existent username
        success, user, error = AuthService.authenticate_user(
            username="nonexistent",
            password="anypassword"
        )
        
        # Assert authentication failed
        assert success is False
        assert user is None
        assert error == "Invalid username or password"
    
    def test_authenticate_generic_error_messages(self, app, db):
        """Test that error messages are generic to prevent username enumeration"""
        # Register a user
        AuthService.register_user(
            username="existinguser",
            email="test@example.com",
            password="password123",
            gender="Male"
        )
        
        # Test 1: Wrong password for existing user
        success1, user1, error1 = AuthService.authenticate_user(
            username="existinguser",
            password="wrongpassword"
        )
        
        # Test 2: Non-existent username
        success2, user2, error2 = AuthService.authenticate_user(
            username="nonexistentuser",
            password="anypassword"
        )
        
        # Assert both return the same generic error message
        # This prevents attackers from determining if a username exists
        assert error1 == error2
        assert error1 == "Invalid username or password"
        assert error2 == "Invalid username or password"
    
    def test_authenticate_user_sql_injection_attempt(self, app, db):
        """Test that SQL injection attempts in username are treated as literal strings"""
        # Register a normal user
        AuthService.register_user(
            username="admin",
            email="admin@example.com",
            password="adminpass",
            gender="Male"
        )
        
        # Try to authenticate with SQL injection pattern
        sql_injection_patterns = [
            "admin' OR '1'='1",
            "admin'--",
            "' OR 1=1--",
            "admin' OR '1'='1' /*",
        ]
        
        for pattern in sql_injection_patterns:
            success, user, error = AuthService.authenticate_user(
                username=pattern,
                password="anypassword"
            )
            
            # Assert authentication failed
            # SQL injection pattern should be treated as literal username
            assert success is False
            assert user is None
            assert error == "Invalid username or password"
    
    def test_authenticate_user_password_verification_round_trip(self, app, db):
        """Test password hashing round-trip property"""
        password = "testpassword123"
        
        # Register user
        AuthService.register_user(
            username="testuser",
            email="test@example.com",
            password=password,
            gender="Female"
        )
        
        # Authenticate with correct password
        success, user, error = AuthService.authenticate_user(
            username="testuser",
            password=password
        )
        
        # Assert authentication succeeded (round-trip property)
        assert success is True
        assert user is not None
        
        # Verify password hash can be verified
        assert bcrypt.check_password_hash(user.password, password)


class TestAuthServiceEdgeCases:
    """Test edge cases and error handling"""
    
    def test_register_user_with_special_characters(self, app, db):
        """Test registration with special characters in username"""
        # Register user with special characters
        success, error = AuthService.register_user(
            username="user@#$%",
            email="test@example.com",
            password="password123",
            gender="Male"
        )
        
        # Should succeed - validation is handled by InputValidator
        assert success is True
        
        # Verify user was created
        user = User.query.filter_by(username="user@#$%").first()
        assert user is not None
    
    def test_register_user_with_sql_injection_pattern(self, app, db):
        """Test that SQL injection patterns in username are stored as literal strings"""
        sql_pattern = "admin' OR '1'='1"
        
        # Register user with SQL injection pattern as username
        success, error = AuthService.register_user(
            username=sql_pattern,
            email="test@example.com",
            password="password123",
            gender="Male"
        )
        
        # Should succeed - SQLAlchemy treats it as literal string
        assert success is True
        
        # Verify user was created with exact username
        user = User.query.filter_by(username=sql_pattern).first()
        assert user is not None
        assert user.username == sql_pattern
    
    def test_authenticate_empty_username(self, app, db):
        """Test authentication with empty username"""
        success, user, error = AuthService.authenticate_user(
            username="",
            password="password"
        )
        
        # Should fail with generic error
        assert success is False
        assert user is None
        assert error == "Invalid username or password"
    
    def test_authenticate_empty_password(self, app, db):
        """Test authentication with empty password"""
        # Register user first
        AuthService.register_user(
            username="testuser",
            email="test@example.com",
            password="correctpassword",
            gender="Male"
        )
        
        # Try to authenticate with empty password
        success, user, error = AuthService.authenticate_user(
            username="testuser",
            password=""
        )
        
        # Should fail
        assert success is False
        assert user is None
        assert error == "Invalid username or password"
