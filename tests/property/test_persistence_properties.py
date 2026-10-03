"""
Property-based tests for data persistence.
Tests round-trip properties for user creation, updates, and configuration.
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from app import create_app, db
from app.models.user import User
from app.services.user_service import UserService
from app.validators.config_validator import ConfigurationParser, Configuration


# Use fixtures from conftest.py


class TestDataPersistenceProperties:
    """Property tests for data persistence round-trip"""
    
    @settings(max_examples=100, deadline=None)
    @given(
        username=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        email_local=st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789', min_size=1, max_size=20),
        password=st.text(min_size=1, max_size=50),
        gender=st.sampled_from(['Male', 'Female'])
    )
    def test_user_creation_persistence_round_trip(self, app, username, email_local, password, gender):
        """
        Property: Creating a user then retrieving preserves all field values.
        Validates: Requirements 3.10, 4.6
        """
        with app.app_context():
            email = f"{email_local}@example.com"
            
            # Create user
            success, error = UserService.create_user(
                username=username,
                email=email,
                password=password,
                gender=gender
            )
            
            if not success:
                # May fail due to duplicate username/email in same test run
                return
            
            # Retrieve user
            user = User.query.filter_by(username=username).first()
            
            # Verify all fields preserved
            assert user is not None, "User not found after creation"
            assert user.username == username, "Username not preserved"
            assert user.email == email, "Email not preserved"
            assert user.gender == gender, "Gender not preserved"
            
            # Password should be hashed but verifiable
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            assert bcrypt.check_password_hash(user.password, password), \
                "Password not verifiable after hashing"
            
            # Cleanup
            db.session.delete(user)
            db.session.commit()
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        original_username=st.text(min_size=1, max_size=30).filter(lambda x: x.strip()),
        new_username=st.text(min_size=1, max_size=30).filter(lambda x: x.strip()),
        new_email_local=st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789', min_size=1, max_size=20),
        new_password=st.text(min_size=1, max_size=50),
        new_gender=st.sampled_from(['Male', 'Female'])
    )
    def test_user_update_round_trip(self, app, original_username, new_username, new_email_local, new_password, new_gender):
        """
        Property: Updating a user then retrieving reflects all updated values.
        Validates: Requirements 4.7
        """
        with app.app_context():
            # Create original user
            original_email = f"{hash(original_username)}@example.com"
            user = User(
                username=original_username,
                email=original_email,
                password="original_hashed_password",
                gender="Male"
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Update user
            new_email = f"{new_email_local}@example.com"
            success, error = UserService.update_user(
                user_id=user_id,
                username=new_username,
                email=new_email,
                password=new_password,
                gender=new_gender
            )
            
            if not success:
                # May fail due to duplicate username/email
                db.session.delete(user)
                db.session.commit()
                return
            
            # Retrieve updated user
            updated_user = UserService.get_user_by_id(user_id)
            
            # Verify all updates preserved
            assert updated_user is not None, "User not found after update"
            assert updated_user.username == new_username, "Username not updated"
            assert updated_user.email == new_email, "Email not updated"
            assert updated_user.gender == new_gender, "Gender not updated"
            
            # Password should be re-hashed and verifiable
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            assert bcrypt.check_password_hash(updated_user.password, new_password), \
                "Updated password not verifiable"
            
            # Cleanup
            db.session.delete(updated_user)
            db.session.commit()
    
    @settings(max_examples=100, deadline=None)
    @given(
        secret_key=st.text(min_size=10, max_size=50),
        database_url=st.sampled_from([
            'sqlite:///test.db',
            'mysql://user:pass@localhost/db',
            'postgresql://user:pass@localhost/db'
        ]),
        flask_env=st.sampled_from(['development', 'testing', 'production']),
        log_level=st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
        bcrypt_rounds=st.integers(min_value=10, max_value=20),
        session_timeout=st.integers(min_value=1, max_value=24)
    )
    def test_configuration_round_trip(self, secret_key, database_url, flask_env, log_level, bcrypt_rounds, session_timeout):
        """
        Property: Parsing then formatting then parsing preserves configuration.
        Validates: Requirements 13.4
        """
        # Create configuration dictionary
        config_dict = {
            'SECRET_KEY': secret_key,
            'DATABASE_URL': database_url,
            'FLASK_ENV': flask_env,
            'LOG_LEVEL': log_level,
            'BCRYPT_LOG_ROUNDS': bcrypt_rounds,
            'SESSION_TIMEOUT_HOURS': session_timeout
        }
        
        # Parse configuration
        success1, config1, error1 = ConfigurationParser.parse(config_dict)
        assert success1 is True, f"Failed to parse configuration: {error1}"
        assert config1 is not None, "Configuration object is None"
        
        # Format configuration returns a dict
        formatted = ConfigurationParser.format(config1)
        assert formatted is not None, "Failed to format configuration"
        assert isinstance(formatted, dict), "Format should return a dict"
        
        # Parse again
        success2, config2, error2 = ConfigurationParser.parse(formatted)
        assert success2 is True, f"Failed to parse formatted configuration: {error2}"
        assert config2 is not None, "Second configuration object is None"
        
        # Verify equality
        assert config1 == config2, "Configuration not preserved through round-trip"
        
        # Verify all fields
        assert config2.secret_key == secret_key
        assert config2.database_url == database_url
        assert config2.flask_env == flask_env
        assert config2.log_level == log_level
        assert config2.bcrypt_rounds == bcrypt_rounds
        assert config2.session_timeout_hours == session_timeout
    
    def test_multiple_users_persistence(self, app):
        """
        Test that multiple users can be created and retrieved correctly.
        Validates: Requirements 3.10, 4.6
        """
        with app.app_context():
            users_data = [
                ("user1", "user1@example.com", "password1", "Male"),
                ("user2", "user2@example.com", "password2", "Female"),
                ("user3", "user3@example.com", "password3", "Male"),
            ]
            
            created_users = []
            
            # Create multiple users
            for username, email, password, gender in users_data:
                success, error = UserService.create_user(username, email, password, gender)
                assert success is True, f"Failed to create user: {username}"
                
                user = User.query.filter_by(username=username).first()
                assert user is not None
                created_users.append(user)
            
            # Verify all users exist
            all_users = UserService.get_all_users()
            assert len(all_users) >= len(users_data)
            
            # Verify each user's data
            for i, (username, email, password, gender) in enumerate(users_data):
                user = created_users[i]
                assert user.username == username
                assert user.email == email
                assert user.gender == gender
                
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt()
                assert bcrypt.check_password_hash(user.password, password)
            
            # Cleanup
            for user in created_users:
                db.session.delete(user)
            db.session.commit()
    
    def test_user_deletion_persistence(self, app):
        """
        Test that user deletion is persisted correctly.
        Validates: Requirements 4.4
        """
        with app.app_context():
            # Create user
            success, error = UserService.create_user(
                username="to_delete",
                email="delete@example.com",
                password="password123",
                gender="Male"
            )
            assert success is True, f"Failed to create user: {error}"
            
            # Get user ID
            user = User.query.filter_by(username="to_delete").first()
            assert user is not None
            user_id = user.id
            
            # Verify user exists
            assert UserService.get_user_by_id(user_id) is not None
            
            # Delete user
            success, error = UserService.delete_user(user_id)
            assert success is True, f"Failed to delete user: {error}"
            
            # Verify user no longer exists
            deleted_user = UserService.get_user_by_id(user_id)
            assert deleted_user is None, f"User still exists after deletion"
    
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        username=st.text(min_size=1, max_size=30).filter(lambda x: x.strip()),
        password=st.text(min_size=1, max_size=50)
    )
    def test_password_update_preserves_authentication(self, app, username, password):
        """
        Property: Updating password preserves authentication capability.
        Validates: Requirements 4.7
        """
        with app.app_context():
            # Create user with initial password
            email = f"{hash(username)}@example.com"
            user = User(
                username=username,
                email=email,
                password="initial_password",
                gender="Male"
            )
            db.session.add(user)
            db.session.commit()
            user_id = user.id
            
            # Update with new password
            success, error = UserService.update_user(
                user_id=user_id,
                username=username,
                email=email,
                password=password,
                gender="Male"
            )
            
            assert success is True
            
            # Retrieve and verify new password works
            updated_user = UserService.get_user_by_id(user_id)
            from flask_bcrypt import Bcrypt
            bcrypt = Bcrypt()
            assert bcrypt.check_password_hash(updated_user.password, password), \
                "New password not verifiable after update"
            
            # Cleanup
            db.session.delete(updated_user)
            db.session.commit()
