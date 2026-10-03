"""
Unit tests for authentication blueprint.
Tests login, register, and logout routes with input validation.
"""
import pytest
from app import db
from app.models.user import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


@pytest.fixture
def sample_user(app):
    """Create a sample user for testing"""
    with app.app_context():
        hashed_password = bcrypt.generate_password_hash('testpassword', rounds=12).decode('utf-8')
        user = User(
            username='testuser',
            email='test@example.com',
            password=hashed_password,
            gender='Male'
        )
        db.session.add(user)
        db.session.commit()
        return user


class TestLoginRoute:
    """Tests for login route"""
    
    def test_login_get_displays_form(self, client):
        """Test GET request displays login form"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'Login' in response.data
        assert b'username' in response.data
        assert b'password' in response.data
    
    def test_login_with_valid_credentials(self, client, sample_user):
        """Test login with valid credentials"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome back' in response.data
    
    def test_login_with_invalid_username(self, client):
        """Test login with non-existent username"""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_login_with_invalid_password(self, client, sample_user):
        """Test login with wrong password"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid username or password' in response.data
    
    def test_login_with_empty_username(self, client):
        """Test login with empty username"""
        response = client.post('/auth/login', data={
            'username': '',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username is required' in response.data
    
    def test_login_with_empty_password(self, client):
        """Test login with empty password"""
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': ''
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Password is required' in response.data
    
    def test_login_with_whitespace_username(self, client):
        """Test login with whitespace-only username"""
        response = client.post('/auth/login', data={
            'username': '   ',
            'password': 'password123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username is required' in response.data
    
    def test_login_creates_session(self, client, sample_user):
        """Test login creates session with user data"""
        with client:
            response = client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            
            # Check session data
            from flask import session
            assert 'user_id' in session
            assert 'username' in session
            assert session['username'] == 'testuser'


class TestRegisterRoute:
    """Tests for register route"""
    
    def test_register_get_displays_form(self, client):
        """Test GET request displays registration form"""
        response = client.get('/auth/register')
        assert response.status_code == 200
        assert b'Register' in response.data
        assert b'username' in response.data
        assert b'email' in response.data
        assert b'password' in response.data
        assert b'gender' in response.data
    
    def test_register_with_valid_data(self, client):
        """Test registration with valid data"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
    
    def test_register_with_duplicate_username(self, client, sample_user):
        """Test registration with existing username"""
        response = client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data
    
    def test_register_with_duplicate_email(self, client, sample_user):
        """Test registration with existing email"""
        response = client.post('/auth/register', data={
            'username': 'differentuser',
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Email already registered' in response.data
    
    def test_register_with_empty_username(self, client):
        """Test registration with empty username"""
        response = client.post('/auth/register', data={
            'username': '',
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username is required' in response.data
    
    def test_register_with_invalid_email(self, client):
        """Test registration with invalid email format"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'notanemail',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid email format' in response.data
    
    def test_register_with_empty_password(self, client):
        """Test registration with empty password"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'test@example.com',
            'password': '',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Password is required' in response.data
    
    def test_register_with_invalid_gender(self, client):
        """Test registration with invalid gender"""
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Other'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Gender must be one of' in response.data
    
    def test_register_with_long_username(self, client):
        """Test registration with username exceeding max length"""
        long_username = 'a' * 201
        response = client.post('/auth/register', data={
            'username': long_username,
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'200 characters or less' in response.data
    
    def test_register_with_long_email(self, client):
        """Test registration with email exceeding max length"""
        long_email = 'a' * 190 + '@example.com'
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': long_email,
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'200 characters or less' in response.data
    
    def test_register_with_long_password(self, client):
        """Test registration with password exceeding max length"""
        long_password = 'a' * 201
        response = client.post('/auth/register', data={
            'username': 'newuser',
            'email': 'test@example.com',
            'password': long_password,
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'200 characters or less' in response.data
    
    def test_register_with_multiple_validation_errors(self, client):
        """Test registration with multiple validation errors"""
        response = client.post('/auth/register', data={
            'username': '',
            'email': 'notanemail',
            'password': '',
            'gender': 'Invalid'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        # Should display multiple error messages
        assert b'Username is required' in response.data
        assert b'Invalid email format' in response.data
        assert b'Password is required' in response.data
        assert b'Gender must be one of' in response.data


class TestLogoutRoute:
    """Tests for logout route"""
    
    def test_logout_clears_session(self, client, sample_user):
        """Test logout clears session data"""
        with client:
            # Login first
            client.post('/auth/login', data={
                'username': 'testuser',
                'password': 'testpassword'
            })
            
            # Verify session exists
            from flask import session
            assert 'user_id' in session
            
            # Logout
            response = client.get('/auth/logout', follow_redirects=True)
            
            assert response.status_code == 200
            assert b'logged out successfully' in response.data
            
            # Verify session is cleared
            assert 'user_id' not in session
            assert 'username' not in session
    
    def test_logout_redirects_to_login(self, client):
        """Test logout redirects to login page"""
        response = client.get('/auth/logout', follow_redirects=True)
        assert response.status_code == 200
        assert b'Login' in response.data


class TestAuthenticationFlow:
    """Integration tests for complete authentication flow"""
    
    def test_complete_registration_and_login_flow(self, client):
        """Test complete flow: register -> login -> logout"""
        # Register
        response = client.post('/auth/register', data={
            'username': 'flowuser',
            'email': 'flow@example.com',
            'password': 'flowpassword',
            'gender': 'Female'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Registration successful' in response.data
        
        # Login
        response = client.post('/auth/login', data={
            'username': 'flowuser',
            'password': 'flowpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Welcome back' in response.data
        
        # Logout
        response = client.get('/auth/logout', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'logged out successfully' in response.data
