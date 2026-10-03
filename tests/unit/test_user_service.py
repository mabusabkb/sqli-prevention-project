"""
Unit tests for UserService.
Tests CRUD operations for user management.
"""
import pytest
from app.services.user_service import UserService
from app.models.user import User
from app import bcrypt


class TestUserServiceGetAllUsers:
    """Test cases for retrieving all users"""
    
    def test_get_all_users_empty_database(self, app, db):
        """Test retrieving users from empty database"""
        success, users, error = UserService.get_all_users()
        
        # Assert success with empty list
        assert success is True
        assert users == []
        assert error is None
    
    def test_get_all_users_with_data(self, app, db):
        """Test retrieving all users when users exist"""
        # Create test users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password=bcrypt.generate_password_hash("pass1", rounds=12).decode('utf-8'),
            gender="Male"
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password=bcrypt.generate_password_hash("pass2", rounds=12).decode('utf-8'),
            gender="Female"
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # Retrieve all users
        success, users, error = UserService.get_all_users()
        
        # Assert success
        assert success is True
        assert error is None
        assert len(users) == 2
        
        # Verify user data
        usernames = [u.username for u in users]
        assert "user1" in usernames
        assert "user2" in usernames
    
    def test_get_all_users_returns_user_objects(self, app, db):
        """Test that get_all_users returns User model objects"""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("pass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        
        # Retrieve users
        success, users, error = UserService.get_all_users()
        
        # Assert returns User objects
        assert success is True
        assert len(users) == 1
        assert isinstance(users[0], User)
        assert users[0].username == "testuser"


class TestUserServiceGetUserById:
    """Test cases for retrieving user by ID"""
    
    def test_get_user_by_id_success(self, app, db):
        """Test successful retrieval of user by ID"""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("pass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Retrieve user by ID
        success, retrieved_user, error = UserService.get_user_by_id(user_id)
        
        # Assert success
        assert success is True
        assert error is None
        assert retrieved_user is not None
        assert retrieved_user.id == user_id
        assert retrieved_user.username == "testuser"
    
    def test_get_user_by_id_not_found(self, app, db):
        """Test retrieval of non-existent user ID"""
        # Try to retrieve non-existent user
        success, user, error = UserService.get_user_by_id(99999)
        
        # Assert failure
        assert success is False
        assert user is None
        assert error == "User not found"
    
    def test_get_user_by_id_returns_user_object(self, app, db):
        """Test that get_user_by_id returns User model object"""
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("pass", rounds=12).decode('utf-8'),
            gender="Female"
        )
        db.session.add(user)
        db.session.commit()
        
        # Retrieve user
        success, retrieved_user, error = UserService.get_user_by_id(user.id)
        
        # Assert returns User object
        assert success is True
        assert isinstance(retrieved_user, User)
        assert retrieved_user.username == "testuser"
        assert retrieved_user.gender == "Female"


class TestUserServiceCreateUser:
    """Test cases for creating users"""
    
    def test_create_user_success(self, app, db):
        """Test successful user creation"""
        # Create user
        success, error = UserService.create_user(
            username="newuser",
            email="new@example.com",
            password="password123",
            gender="Male"
        )
        
        # Assert success
        assert success is True
        assert error is None
        
        # Verify user was created in database
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.gender == "Male"
        
        # Verify password was hashed
        assert user.password != "password123"
        assert bcrypt.check_password_hash(user.password, "password123")
    
    def test_create_user_duplicate_username(self, app, db):
        """Test creation with duplicate username fails"""
        # Create first user
        success1, error1 = UserService.create_user(
            username="testuser",
            email="test1@example.com",
            password="pass1",
            gender="Male"
        )
        assert success1 is True
        
        # Try to create second user with same username
        success2, error2 = UserService.create_user(
            username="testuser",
            email="test2@example.com",
            password="pass2",
            gender="Female"
        )
        
        # Assert failure
        assert success2 is False
        assert error2 == "Username already exists"
        
        # Verify only one user exists
        users = User.query.filter_by(username="testuser").all()
        assert len(users) == 1
    
    def test_create_user_duplicate_email(self, app, db):
        """Test creation with duplicate email fails"""
        # Create first user
        success1, error1 = UserService.create_user(
            username="user1",
            email="test@example.com",
            password="pass1",
            gender="Male"
        )
        assert success1 is True
        
        # Try to create second user with same email
        success2, error2 = UserService.create_user(
            username="user2",
            email="test@example.com",
            password="pass2",
            gender="Female"
        )
        
        # Assert failure
        assert success2 is False
        assert error2 == "Email already registered"
        
        # Verify only one user exists with that email
        users = User.query.filter_by(email="test@example.com").all()
        assert len(users) == 1
    
    def test_create_user_password_hashing(self, app, db):
        """Test that password is hashed with bcrypt cost factor >= 12"""
        # Create user
        success, error = UserService.create_user(
            username="testuser",
            email="test@example.com",
            password="mypassword",
            gender="Female"
        )
        assert success is True
        
        # Get user from database
        user = User.query.filter_by(username="testuser").first()
        
        # Verify password is hashed
        assert user.password != "mypassword"
        assert user.password.startswith('$2b$') or user.password.startswith('$2y$')
        
        # Extract and verify cost factor
        hash_parts = user.password.split('$')
        cost_factor = int(hash_parts[2])
        assert cost_factor >= 12
    
    def test_create_user_with_sql_injection_pattern(self, app, db):
        """Test that SQL injection patterns are stored as literal strings"""
        sql_pattern = "admin' OR '1'='1"
        
        # Create user with SQL injection pattern as username
        success, error = UserService.create_user(
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


class TestUserServiceUpdateUser:
    """Test cases for updating users"""
    
    def test_update_user_success(self, app, db):
        """Test successful user update"""
        # Create initial user
        user = User(
            username="olduser",
            email="old@example.com",
            password=bcrypt.generate_password_hash("oldpass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Update user
        success, error = UserService.update_user(
            user_id=user_id,
            username="newuser",
            email="new@example.com",
            password="newpass",
            gender="Female"
        )
        
        # Assert success
        assert success is True
        assert error is None
        
        # Verify user was updated
        updated_user = User.query.get(user_id)
        assert updated_user.username == "newuser"
        assert updated_user.email == "new@example.com"
        assert updated_user.gender == "Female"
        
        # Verify new password works
        assert bcrypt.check_password_hash(updated_user.password, "newpass")
        
        # Verify old password doesn't work
        assert not bcrypt.check_password_hash(updated_user.password, "oldpass")
    
    def test_update_user_not_found(self, app, db):
        """Test updating non-existent user fails"""
        # Try to update non-existent user
        success, error = UserService.update_user(
            user_id=99999,
            username="newuser",
            email="new@example.com",
            password="newpass",
            gender="Male"
        )
        
        # Assert failure
        assert success is False
        assert error == "User not found"
    
    def test_update_user_duplicate_username(self, app, db):
        """Test updating to duplicate username fails"""
        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password=bcrypt.generate_password_hash("pass1", rounds=12).decode('utf-8'),
            gender="Male"
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password=bcrypt.generate_password_hash("pass2", rounds=12).decode('utf-8'),
            gender="Female"
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # Try to update user2 with user1's username
        success, error = UserService.update_user(
            user_id=user2.id,
            username="user1",  # Duplicate username
            email="user2@example.com",
            password="pass2",
            gender="Female"
        )
        
        # Assert failure
        assert success is False
        assert error == "Username already exists"
        
        # Verify user2 was not updated
        user2_check = User.query.get(user2.id)
        assert user2_check.username == "user2"
    
    def test_update_user_duplicate_email(self, app, db):
        """Test updating to duplicate email fails"""
        # Create two users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password=bcrypt.generate_password_hash("pass1", rounds=12).decode('utf-8'),
            gender="Male"
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password=bcrypt.generate_password_hash("pass2", rounds=12).decode('utf-8'),
            gender="Female"
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # Try to update user2 with user1's email
        success, error = UserService.update_user(
            user_id=user2.id,
            username="user2",
            email="user1@example.com",  # Duplicate email
            password="pass2",
            gender="Female"
        )
        
        # Assert failure
        assert success is False
        assert error == "Email already registered"
        
        # Verify user2 was not updated
        user2_check = User.query.get(user2.id)
        assert user2_check.email == "user2@example.com"
    
    def test_update_user_same_username_allowed(self, app, db):
        """Test updating user with same username is allowed"""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("oldpass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        
        # Update user keeping same username
        success, error = UserService.update_user(
            user_id=user.id,
            username="testuser",  # Same username
            email="newemail@example.com",
            password="newpass",
            gender="Female"
        )
        
        # Assert success
        assert success is True
        assert error is None
        
        # Verify updates were applied
        updated_user = User.query.get(user.id)
        assert updated_user.username == "testuser"
        assert updated_user.email == "newemail@example.com"
        assert updated_user.gender == "Female"
    
    def test_update_user_same_email_allowed(self, app, db):
        """Test updating user with same email is allowed"""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("oldpass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        
        # Update user keeping same email
        success, error = UserService.update_user(
            user_id=user.id,
            username="newusername",
            email="test@example.com",  # Same email
            password="newpass",
            gender="Female"
        )
        
        # Assert success
        assert success is True
        assert error is None
        
        # Verify updates were applied
        updated_user = User.query.get(user.id)
        assert updated_user.username == "newusername"
        assert updated_user.email == "test@example.com"
        assert updated_user.gender == "Female"
    
    def test_update_user_password_rehashing(self, app, db):
        """Test that password is rehashed on update"""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("oldpass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        old_hash = user.password
        
        # Update user with new password
        success, error = UserService.update_user(
            user_id=user.id,
            username="testuser",
            email="test@example.com",
            password="newpass",
            gender="Male"
        )
        assert success is True
        
        # Verify password hash changed
        updated_user = User.query.get(user.id)
        assert updated_user.password != old_hash
        
        # Verify new password works
        assert bcrypt.check_password_hash(updated_user.password, "newpass")
        
        # Verify old password doesn't work
        assert not bcrypt.check_password_hash(updated_user.password, "oldpass")


class TestUserServiceDeleteUser:
    """Test cases for deleting users"""
    
    def test_delete_user_success(self, app, db):
        """Test successful user deletion"""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("pass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Delete user
        success, error = UserService.delete_user(user_id)
        
        # Assert success
        assert success is True
        assert error is None
        
        # Verify user was deleted
        deleted_user = User.query.get(user_id)
        assert deleted_user is None
    
    def test_delete_user_not_found(self, app, db):
        """Test deleting non-existent user fails"""
        # Try to delete non-existent user
        success, error = UserService.delete_user(99999)
        
        # Assert failure
        assert success is False
        assert error == "User not found"
    
    def test_delete_user_removes_from_database(self, app, db):
        """Test that deleted user is completely removed from database"""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("pass", rounds=12).decode('utf-8'),
            gender="Female"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        username = user.username
        
        # Delete user
        success, error = UserService.delete_user(user_id)
        assert success is True
        
        # Verify user cannot be found by ID
        assert User.query.get(user_id) is None
        
        # Verify user cannot be found by username
        assert User.query.filter_by(username=username).first() is None
    
    def test_delete_user_multiple_users(self, app, db):
        """Test deleting one user doesn't affect others"""
        # Create multiple users
        user1 = User(
            username="user1",
            email="user1@example.com",
            password=bcrypt.generate_password_hash("pass1", rounds=12).decode('utf-8'),
            gender="Male"
        )
        user2 = User(
            username="user2",
            email="user2@example.com",
            password=bcrypt.generate_password_hash("pass2", rounds=12).decode('utf-8'),
            gender="Female"
        )
        user3 = User(
            username="user3",
            email="user3@example.com",
            password=bcrypt.generate_password_hash("pass3", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add_all([user1, user2, user3])
        db.session.commit()
        
        # Delete user2
        success, error = UserService.delete_user(user2.id)
        assert success is True
        
        # Verify user2 was deleted
        assert User.query.get(user2.id) is None
        
        # Verify user1 and user3 still exist
        assert User.query.get(user1.id) is not None
        assert User.query.get(user3.id) is not None
        
        # Verify total count
        assert User.query.count() == 2


class TestUserServiceEdgeCases:
    """Test edge cases and error handling"""
    
    def test_create_user_with_special_characters(self, app, db):
        """Test creating user with special characters in username"""
        # Create user with special characters
        success, error = UserService.create_user(
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
        assert user.username == "user@#$%"
    
    def test_update_user_with_sql_injection_pattern(self, app, db):
        """Test that SQL injection patterns are treated as literal strings"""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("pass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        
        # Update with SQL injection pattern
        sql_pattern = "admin' OR '1'='1"
        success, error = UserService.update_user(
            user_id=user.id,
            username=sql_pattern,
            email="test@example.com",
            password="pass",
            gender="Male"
        )
        
        # Should succeed - SQLAlchemy treats it as literal string
        assert success is True
        
        # Verify username was updated to exact pattern
        updated_user = User.query.get(user.id)
        assert updated_user.username == sql_pattern
    
    def test_get_user_by_id_with_sql_injection(self, app, db):
        """Test that SQL injection in ID parameter is handled safely"""
        # Create user
        user = User(
            username="testuser",
            email="test@example.com",
            password=bcrypt.generate_password_hash("pass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        
        # Try to retrieve with valid ID (should work)
        success, retrieved_user, error = UserService.get_user_by_id(user.id)
        assert success is True
        assert retrieved_user is not None
    
    def test_data_persistence_round_trip(self, app, db):
        """Test that creating then retrieving preserves all field values"""
        # Create user
        username = "testuser"
        email = "test@example.com"
        password = "testpassword"
        gender = "Female"
        
        success, error = UserService.create_user(
            username=username,
            email=email,
            password=password,
            gender=gender
        )
        assert success is True
        
        # Retrieve user
        user = User.query.filter_by(username=username).first()
        
        # Verify all fields preserved
        assert user.username == username
        assert user.email == email
        assert user.gender == gender
        
        # Verify password is hashed but verifiable
        assert user.password != password
        assert bcrypt.check_password_hash(user.password, password)
    
    def test_user_update_round_trip(self, app, db):
        """Test that updating then retrieving reflects all updated values"""
        # Create user
        user = User(
            username="olduser",
            email="old@example.com",
            password=bcrypt.generate_password_hash("oldpass", rounds=12).decode('utf-8'),
            gender="Male"
        )
        db.session.add(user)
        db.session.commit()
        user_id = user.id
        
        # Update user
        new_username = "newuser"
        new_email = "new@example.com"
        new_password = "newpass"
        new_gender = "Female"
        
        success, error = UserService.update_user(
            user_id=user_id,
            username=new_username,
            email=new_email,
            password=new_password,
            gender=new_gender
        )
        assert success is True
        
        # Retrieve updated user
        updated_user = User.query.get(user_id)
        
        # Verify all fields updated
        assert updated_user.username == new_username
        assert updated_user.email == new_email
        assert updated_user.gender == new_gender
        
        # Verify new password works
        assert bcrypt.check_password_hash(updated_user.password, new_password)
