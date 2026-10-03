"""
Unit tests for secure session management.
Tests session configuration, timeout, and security settings.
"""
import pytest
from datetime import timedelta
from flask import session
from app import create_app
from app.models.user import User
from app import db


class TestSessionManagement:
    """Test suite for session management security"""
    
    def test_session_cookie_httponly_enabled(self):
        """Test that HttpOnly flag is enabled for session cookies"""
        app = create_app('testing')
        assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    
    def test_session_cookie_samesite_configured(self):
        """Test that SameSite attribute is configured"""
        app = create_app('testing')
        assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
    
    def test_session_timeout_configured(self):
        """Test that session timeout is set to 1 hour"""
        app = create_app('testing')
        assert app.config['PERMANENT_SESSION_LIFETIME'] == timedelta(hours=1)
    
    def test_session_cookie_secure_in_production(self):
        """Test that Secure flag is enabled in production"""
        # Import the config class directly to check the setting
        from config import ProductionConfig
        assert ProductionConfig.SESSION_COOKIE_SECURE is True
    
    def test_session_cookie_not_secure_in_development(self):
        """Test that Secure flag is disabled in development (for local testing)"""
        app = create_app('development')
        assert app.config['SESSION_COOKIE_SECURE'] is False
    
    def test_login_stores_user_data_in_session(self, client, test_user):
        """Test that successful login stores user_id and username in session"""
        # Login with test user
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=False)
        
        # Check that session contains user data
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'username' in sess
            assert sess['username'] == 'testuser'
    
    def test_session_marked_as_permanent(self, client, test_user):
        """Test that session is marked as permanent to enforce timeout"""
        # Login with test user
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=False)
        
        # Check that session is permanent
        with client.session_transaction() as sess:
            # Flask stores permanent flag in session
            assert sess.permanent is True
    
    def test_logout_clears_session(self, client, test_user):
        """Test that logout clears all session data"""
        # Login first
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Verify session has data
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'username' in sess
        
        # Logout
        client.get('/auth/logout')
        
        # Verify session is cleared
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'username' not in sess
    
    def test_session_data_persists_across_requests(self, client, test_user):
        """Test that session data persists across multiple requests"""
        # Login
        client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        # Make another request
        response = client.get('/users/')
        
        # Session should still contain user data
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'username' in sess
            assert sess['username'] == 'testuser'
    
    def test_failed_login_does_not_create_session(self, client, test_user):
        """Test that failed login does not create session data"""
        # Attempt login with wrong password
        response = client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        # Session should not contain user data
        with client.session_transaction() as sess:
            assert 'user_id' not in sess
            assert 'username' not in sess


@pytest.fixture
def test_user(client):
    """Create a test user for authentication tests"""
    from app.services.auth_service import AuthService
    
    # Register a test user
    AuthService.register_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        gender='Male'
    )
    
    yield
    
    # Cleanup is handled by conftest.py's app fixture
