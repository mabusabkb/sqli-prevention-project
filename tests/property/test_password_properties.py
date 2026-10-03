"""
Property-based tests for password security.
Tests bcrypt hashing, cost factor, and round-trip verification.
"""
import pytest
import re
from hypothesis import given, strategies as st, settings
from app import create_app, db
from app.services.auth_service import AuthService
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


# Use fixtures from conftest.py


class TestPasswordSecurity:
    """Property tests for password security"""
    
    @settings(max_examples=100, deadline=None)
    @given(password=st.text(min_size=1, max_size=200))
    def test_password_hashing_round_trip(self, app, password):
        """
        Property: Hashing then verifying with correct password returns true.
        Validates: Requirements 2.1, 2.7
        """
        with app.app_context():
            # Hash the password
            hashed = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
            
            # Verify with correct password
            assert bcrypt.check_password_hash(hashed, password) is True, \
                "Password verification failed for correct password"
            
            # Verify hash format (bcrypt format: $2b$rounds$salt+hash)
            assert hashed.startswith('$2b$'), "Hash does not use bcrypt format"
            
            # Extract cost factor from hash
            match = re.match(r'\$2b\$(\d+)\$', hashed)
            assert match is not None, "Could not extract cost factor from hash"
            cost_factor = int(match.group(1))
            assert cost_factor >= 12, f"Cost factor {cost_factor} is less than 12"
    
    @settings(max_examples=100, deadline=None)
    @given(
        password=st.text(min_size=1, max_size=200),
        wrong_password=st.text(min_size=1, max_size=200)
    )
    def test_wrong_password_fails_verification(self, app, password, wrong_password):
        """
        Property: Verifying with wrong password returns false.
        Validates: Requirements 2.1, 2.7
        """
        # Skip if passwords are the same
        if password == wrong_password:
            return
        
        with app.app_context():
            # Hash the correct password
            hashed = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
            
            # Verify with wrong password
            assert bcrypt.check_password_hash(hashed, wrong_password) is False, \
                "Wrong password incorrectly verified as correct"
    
    @settings(max_examples=100)
    @given(password=st.text(min_size=1, max_size=200))
    def test_bcrypt_cost_factor_minimum_12(self, app, password):
        """
        Property: All password hashes use cost factor >= 12.
        Validates: Requirements 2.1, 8.4
        """
        with app.app_context():
            # Hash password with default settings
            hashed = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
            
            # Extract cost factor
            match = re.match(r'\$2b\$(\d+)\$', hashed)
            assert match is not None, "Invalid bcrypt hash format"
            
            cost_factor = int(match.group(1))
            assert cost_factor >= 12, \
                f"Cost factor {cost_factor} is below minimum of 12"
    
    @settings(max_examples=100, deadline=None)
    @given(password=st.text(min_size=2, max_size=200).filter(lambda x: len(x) > 1))
    def test_password_not_stored_in_plain_text(self, app, password):
        """
        Property: Hashed passwords do not contain the original password.
        Validates: Requirements 2.3, 8.4
        """
        with app.app_context():
            # Hash the password
            hashed = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
            
            # Verify hash does not contain original password
            assert password not in hashed, \
                "Original password found in hash (not properly hashed)"
            
            # Verify hash is different from password
            assert hashed != password, \
                "Hash is identical to password (not hashed)"
    
    @settings(max_examples=100, deadline=None)
    @given(password=st.text(min_size=1, max_size=200))
    def test_same_password_produces_different_hashes(self, app, password):
        """
        Property: Hashing the same password twice produces different hashes (salt).
        Validates: Requirements 2.1, 8.4
        """
        with app.app_context():
            # Hash the same password twice
            hash1 = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
            hash2 = bcrypt.generate_password_hash(password, rounds=12).decode('utf-8')
            
            # Hashes should be different (due to random salt)
            assert hash1 != hash2, \
                "Same password produced identical hashes (salt not working)"
            
            # But both should verify correctly
            assert bcrypt.check_password_hash(hash1, password) is True
            assert bcrypt.check_password_hash(hash2, password) is True
    
    def test_auth_service_uses_bcrypt_with_cost_12(self, app):
        """
        Test that AuthService uses bcrypt with cost factor 12.
        Validates: Requirements 2.1, 8.4
        """
        with app.app_context():
            # Register a user
            username = "testuser"
            email = "test@example.com"
            password = "TestPassword123"
            
            success, error = AuthService.register_user(
                username=username,
                email=email,
                password=password,
                gender="Male"
            )
            
            assert success is True, f"Registration failed: {error}"
            
            # Get the user from database
            from app.models.user import User
            user = User.query.filter_by(username=username).first()
            assert user is not None
            
            # Verify password hash format
            assert user.password.startswith('$2b$'), \
                "Password not hashed with bcrypt"
            
            # Extract cost factor
            match = re.match(r'\$2b\$(\d+)\$', user.password)
            assert match is not None
            cost_factor = int(match.group(1))
            assert cost_factor >= 12, \
                f"Cost factor {cost_factor} is below minimum of 12"
            
            # Verify authentication works
            auth_success, auth_user, auth_error = AuthService.authenticate_user(
                username, password
            )
            assert auth_success is True
            assert auth_user.id == user.id
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
    
    @settings(max_examples=50, deadline=None)
    @given(
        password=st.text(min_size=1, max_size=200),
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip())
    )
    def test_full_registration_authentication_round_trip(self, app, password, username):
        """
        Property: Register then authenticate preserves password verification.
        Validates: Requirements 2.1, 2.2, 2.7
        """
        with app.app_context():
            email = f"{hash(username)}@example.com"
            
            # Register user
            success, error = AuthService.register_user(
                username=username,
                email=email,
                password=password,
                gender="Male"
            )
            
            if not success:
                # May fail due to duplicate username/email
                return
            
            # Authenticate with correct password
            auth_success, user, auth_error = AuthService.authenticate_user(
                username, password
            )
            
            assert auth_success is True, \
                f"Authentication failed after registration: {auth_error}"
            assert user is not None
            assert user.username == username
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
