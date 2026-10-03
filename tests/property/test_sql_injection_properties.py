"""
Property-based tests for SQL injection prevention.
Tests that SQLAlchemy ORM treats SQL injection attempts as literal strings.
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app import create_app, db
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.user_service import UserService


# Common SQL injection patterns
SQL_INJECTION_PATTERNS = [
    "' OR '1'='1",
    "admin'--",
    "' OR 1=1--",
    "' UNION SELECT NULL--",
    "'; DROP TABLE users--",
    "' OR 'x'='x",
    "1' AND '1'='1",
    "' OR ''='",
    "admin' OR '1'='1'--",
    "' UNION SELECT * FROM users--",
    "1'; DROP TABLE users; --",
    "' OR 1=1#",
    "admin'/*",
    "' OR 'a'='a",
    "') OR ('1'='1",
]


# Use fixtures from conftest.py


class TestSQLInjectionPrevention:
    """Property tests for SQL injection prevention"""
    
    @settings(max_examples=100, deadline=None)
    @given(injection_pattern=st.sampled_from(SQL_INJECTION_PATTERNS))
    def test_sql_injection_in_username_treated_as_literal(self, app, injection_pattern):
        """
        Property: SQL injection patterns in username are treated as literal strings.
        Validates: Requirements 1.4, 1.5, 8.3, 8.7
        """
        with app.app_context():
            # Create a user with SQL injection pattern as username
            email = f"test_{hash(injection_pattern)}@example.com"
            password = "TestPassword123"
            
            # Register user with injection pattern in username
            success, error = AuthService.register_user(
                username=injection_pattern,
                email=email,
                password=password,
                gender="Male"
            )
            
            # Should succeed - injection pattern treated as literal string
            assert success is True, f"Failed to register user with username: {injection_pattern}"
            
            # Verify user was created with exact username (not executed as SQL)
            user = User.query.filter_by(username=injection_pattern).first()
            assert user is not None, "User not found in database"
            assert user.username == injection_pattern, "Username was modified"
            
            # Verify authentication works with injection pattern
            auth_success, auth_user, auth_error = AuthService.authenticate_user(
                injection_pattern, password
            )
            assert auth_success is True, "Authentication failed"
            assert auth_user.username == injection_pattern
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
    
    @settings(max_examples=100)
    @given(injection_pattern=st.sampled_from(SQL_INJECTION_PATTERNS))
    def test_sql_injection_in_email_treated_as_literal(self, app, injection_pattern):
        """
        Property: SQL injection patterns in email are treated as literal strings.
        Validates: Requirements 1.4, 1.5, 8.3, 8.7
        """
        with app.app_context():
            # Create email with injection pattern (may not be valid email format)
            # We'll use a valid email format with injection in local part
            username = f"user_{hash(injection_pattern)}"
            # Email validation will reject most injection patterns, so we test
            # that the validator catches them, not the database
            email_with_injection = f"{injection_pattern}@example.com"
            password = "TestPassword123"
            
            # Try to register - may fail validation but should not cause SQL injection
            try:
                success, error = AuthService.register_user(
                    username=username,
                    email=email_with_injection,
                    password=password,
                    gender="Female"
                )
                
                # If it succeeds (valid email format), verify it's stored literally
                if success:
                    user = User.query.filter_by(email=email_with_injection).first()
                    assert user is not None
                    assert user.email == email_with_injection
                    
                    # Cleanup
                    db.session.delete(user)
                    db.session.commit()
                else:
                    # If it fails, it should be due to validation, not SQL error
                    assert error is not None
                    assert "email" in error.lower() or "invalid" in error.lower()
            except Exception as e:
                # Should not raise SQL-related exceptions
                assert "sql" not in str(e).lower(), f"SQL error occurred: {e}"
    
    @settings(max_examples=100)
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        injection_suffix=st.sampled_from(SQL_INJECTION_PATTERNS)
    )
    def test_sql_injection_appended_to_valid_username(self, app, username, injection_suffix):
        """
        Property: SQL injection patterns appended to valid usernames are treated literally.
        Validates: Requirements 1.4, 1.5, 8.3, 8.7
        """
        with app.app_context():
            # Combine valid username with injection pattern
            combined_username = username + injection_suffix
            if len(combined_username) > 200:
                combined_username = combined_username[:200]
            
            email = f"test_{hash(combined_username)}@example.com"
            password = "TestPassword123"
            
            # Register user
            success, error = AuthService.register_user(
                username=combined_username,
                email=email,
                password=password,
                gender="Male"
            )
            
            # Should succeed
            assert success is True, f"Failed with username: {combined_username}"
            
            # Verify exact storage
            user = User.query.filter_by(username=combined_username).first()
            assert user is not None
            assert user.username == combined_username
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(injection_pattern=st.sampled_from(SQL_INJECTION_PATTERNS))
    def test_user_query_by_id_with_injection_pattern(self, app, injection_pattern):
        """
        Property: Querying users by ID with injection patterns is safe.
        Validates: Requirements 1.4, 1.5, 8.3, 8.7
        """
        with app.app_context():
            # Create a normal user first
            user = User(
                username="testuser",
                email="test@example.com",
                password="hashed_password",
                gender="Male"
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Try to query with injection pattern (should fail gracefully)
            result = UserService.get_user_by_id(injection_pattern)
            
            # Should return None (invalid ID format), not cause SQL injection
            assert result is None, "Should return None for invalid ID"
            
            # Verify original user still exists
            original_user = UserService.get_user_by_id(user_id)
            assert original_user is not None
            assert original_user.username == "testuser"
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
    
    def test_all_sql_injection_patterns_are_safe(self, app):
        """
        Test all common SQL injection patterns are handled safely.
        Validates: Requirements 8.1, 8.2, 8.3, 8.7
        """
        with app.app_context():
            for i, pattern in enumerate(SQL_INJECTION_PATTERNS):
                username = f"user_{i}_{pattern}"[:200]
                email = f"test{i}@example.com"
                password = "TestPassword123"
                
                # Register user with injection pattern
                success, error = AuthService.register_user(
                    username=username,
                    email=email,
                    password=password,
                    gender="Male"
                )
                
                # Should succeed
                assert success is True, f"Pattern failed: {pattern}"
                
                # Verify user exists with exact username
                user = User.query.filter_by(username=username).first()
                assert user is not None
                assert user.username == username
                
                # Cleanup
                db.session.delete(user)
                db.session.commit()
    
    def test_sql_injection_does_not_bypass_authentication(self, app):
        """
        Test that SQL injection patterns cannot bypass authentication.
        Validates: Requirements 8.2, 8.3
        """
        with app.app_context():
            # Create a legitimate user
            AuthService.register_user(
                username="admin",
                email="admin@example.com",
                password="SecurePassword123",
                gender="Male"
            )
            
            # Try to authenticate with SQL injection patterns
            for pattern in SQL_INJECTION_PATTERNS:
                success, user, error = AuthService.authenticate_user(
                    username=pattern,
                    password="anything"
                )
                
                # Should fail - injection pattern treated as literal username
                assert success is False, f"Authentication bypassed with: {pattern}"
                assert user is None
                assert error is not None
            
            # Cleanup
            user = User.query.filter_by(username="admin").first()
            if user:
                db.session.delete(user)
                db.session.commit()
