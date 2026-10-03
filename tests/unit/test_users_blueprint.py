"""
Unit tests for users management blueprint.
Tests CRUD operations with input validation and authentication.
"""
import pytest
from app import db
from app.models.user import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()


@pytest.fixture
def sample_users(app):
    """Create sample users for testing"""
    with app.app_context():
        users = []
        for i in range(3):
            hashed_password = bcrypt.generate_password_hash(f'password{i}', rounds=12).decode('utf-8')
            user = User(
                username=f'user{i}',
                email=f'user{i}@example.com',
                password=hashed_password,
                gender='Male' if i % 2 == 0 else 'Female'
            )
            db.session.add(user)
        db.session.commit()
        
        # Refresh users to get their IDs before session closes
        user_ids = [User.query.filter_by(username=f'user{i}').first().id for i in range(3)]
        
    # Return user IDs instead of detached objects
    return user_ids


@pytest.fixture
def logged_in_client(client, sample_users):
    """Create a logged-in client session"""
    with client:
        # Login as first user
        client.post('/auth/login', data={
            'username': 'user0',
            'password': 'password0'
        })
        yield client


class TestLoginRequired:
    """Tests for login_required decorator"""
    
    def test_list_users_requires_login(self, client):
        """Test list_users redirects to login when not authenticated"""
        response = client.get('/users/', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
        assert b'Login' in response.data
    
    def test_create_user_requires_login(self, client):
        """Test create_user redirects to login when not authenticated"""
        response = client.get('/users/create', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_update_user_requires_login(self, client, sample_users):
        """Test update_user redirects to login when not authenticated"""
        response = client.get('/users/update/1', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data
    
    def test_delete_user_requires_login(self, client, sample_users):
        """Test delete_user redirects to login when not authenticated"""
        response = client.get('/users/delete/1', follow_redirects=True)
        assert response.status_code == 200
        assert b'Please log in' in response.data


class TestListUsersRoute:
    """Tests for list_users route"""
    
    def test_list_users_displays_all_users(self, logged_in_client, sample_users):
        """Test list_users displays all users in database"""
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert b'Users Management' in response.data
        
        # Check all users are displayed
        for i in range(3):
            assert f'user{i}'.encode() in response.data
            assert f'user{i}@example.com'.encode() in response.data
    
    def test_list_users_displays_empty_message(self, logged_in_client):
        """Test list_users displays message when no users exist"""
        # Clear all users
        with logged_in_client.application.app_context():
            User.query.delete()
            db.session.commit()
        
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert b'No users found' in response.data
    
    def test_list_users_has_create_button(self, logged_in_client, sample_users):
        """Test list_users page has create new user button"""
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert b'Create New User' in response.data
    
    def test_list_users_has_edit_buttons(self, logged_in_client, sample_users):
        """Test list_users page has edit buttons for each user"""
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert response.data.count(b'Edit') >= len(sample_users)
    
    def test_list_users_has_delete_buttons(self, logged_in_client, sample_users):
        """Test list_users page has delete buttons for each user"""
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert response.data.count(b'Delete') >= len(sample_users)
    
    def test_list_users_displays_user_count(self, logged_in_client, sample_users):
        """Test list_users displays total user count"""
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert b'Total Users' in response.data


class TestCreateUserRoute:
    """Tests for create_user route"""
    
    def test_create_user_get_displays_form(self, logged_in_client):
        """Test GET request displays create user form"""
        response = logged_in_client.get('/users/create')
        assert response.status_code == 200
        assert b'Create New User' in response.data
        assert b'username' in response.data
        assert b'email' in response.data
        assert b'password' in response.data
        assert b'gender' in response.data
    
    def test_create_user_with_valid_data(self, logged_in_client):
        """Test creating user with valid data"""
        response = logged_in_client.post('/users/create', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User created successfully' in response.data
        
        # Verify user was created in database
        with logged_in_client.application.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'
            assert user.gender == 'Male'
    
    def test_create_user_with_empty_username(self, logged_in_client):
        """Test creating user with empty username"""
        response = logged_in_client.post('/users/create', data={
            'username': '',
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username is required' in response.data
    
    def test_create_user_with_invalid_email(self, logged_in_client):
        """Test creating user with invalid email format"""
        response = logged_in_client.post('/users/create', data={
            'username': 'testuser',
            'email': 'notanemail',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid email format' in response.data
    
    def test_create_user_with_empty_password(self, logged_in_client):
        """Test creating user with empty password"""
        response = logged_in_client.post('/users/create', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Password is required' in response.data
    
    def test_create_user_with_invalid_gender(self, logged_in_client):
        """Test creating user with invalid gender"""
        response = logged_in_client.post('/users/create', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Other'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Gender must be one of' in response.data
    
    def test_create_user_with_duplicate_username(self, logged_in_client, sample_users):
        """Test creating user with existing username"""
        response = logged_in_client.post('/users/create', data={
            'username': 'user0',
            'email': 'different@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data
    
    def test_create_user_with_duplicate_email(self, logged_in_client, sample_users):
        """Test creating user with existing email"""
        response = logged_in_client.post('/users/create', data={
            'username': 'differentuser',
            'email': 'user0@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Email already registered' in response.data
    
    def test_create_user_with_long_username(self, logged_in_client):
        """Test creating user with username exceeding max length"""
        long_username = 'a' * 201
        response = logged_in_client.post('/users/create', data={
            'username': long_username,
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'200 characters or less' in response.data
    
    def test_create_user_with_long_email(self, logged_in_client):
        """Test creating user with email exceeding max length"""
        long_email = 'a' * 190 + '@example.com'
        response = logged_in_client.post('/users/create', data={
            'username': 'testuser',
            'email': long_email,
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'200 characters or less' in response.data
    
    def test_create_user_with_long_password(self, logged_in_client):
        """Test creating user with password exceeding max length"""
        long_password = 'a' * 201
        response = logged_in_client.post('/users/create', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': long_password,
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'200 characters or less' in response.data
    
    def test_create_user_with_whitespace_username(self, logged_in_client):
        """Test creating user with whitespace-only username"""
        response = logged_in_client.post('/users/create', data={
            'username': '   ',
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username is required' in response.data
    
    def test_create_user_with_multiple_validation_errors(self, logged_in_client):
        """Test creating user with multiple validation errors"""
        response = logged_in_client.post('/users/create', data={
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
    
    def test_create_user_password_is_hashed(self, logged_in_client):
        """Test that created user password is hashed with bcrypt"""
        logged_in_client.post('/users/create', data={
            'username': 'hashtest',
            'email': 'hash@example.com',
            'password': 'plainpassword',
            'gender': 'Male'
        }, follow_redirects=True)
        
        # Verify password is hashed
        with logged_in_client.application.app_context():
            user = User.query.filter_by(username='hashtest').first()
            assert user is not None
            assert user.password != 'plainpassword'
            assert user.password.startswith('$2b$')  # Bcrypt hash format
            assert bcrypt.check_password_hash(user.password, 'plainpassword')


class TestUpdateUserRoute:
    """Tests for update_user route"""
    
    def test_update_user_get_displays_form(self, logged_in_client, sample_users):
        """Test GET request displays update user form with current data"""
        user_id = sample_users[0]  # sample_users now contains IDs
        response = logged_in_client.get(f'/users/update/{user_id}')
        assert response.status_code == 200
        assert b'Update User' in response.data
        assert b'user0' in response.data
        assert b'user0@example.com' in response.data
    
    def test_update_user_with_valid_data(self, logged_in_client, sample_users):
        """Test updating user with valid data"""
        user_id = sample_users[0]  # sample_users now contains IDs
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'updateduser',
            'email': 'updated@example.com',
            'password': 'newpassword',
            'gender': 'Female'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User updated successfully' in response.data
        
        # Verify user was updated in database
        with logged_in_client.application.app_context():
            user = User.query.get(user_id)
            assert user.username == 'updateduser'
            assert user.email == 'updated@example.com'
            assert user.gender == 'Female'
    
    def test_update_user_with_invalid_id(self, logged_in_client):
        """Test updating user with invalid ID"""
        response = logged_in_client.get('/users/update/invalid', follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid user ID' in response.data
    
    def test_update_user_with_nonexistent_id(self, logged_in_client):
        """Test updating user with non-existent ID"""
        response = logged_in_client.get('/users/update/99999', follow_redirects=True)
        assert response.status_code == 200
        assert b'User not found' in response.data
    
    def test_update_user_with_empty_username(self, logged_in_client, sample_users):
        """Test updating user with empty username"""
        user_id = sample_users[0]
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': '',
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username is required' in response.data
    
    def test_update_user_with_invalid_email(self, logged_in_client, sample_users):
        """Test updating user with invalid email format"""
        user_id = sample_users[0]
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'testuser',
            'email': 'notanemail',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Invalid email format' in response.data
    
    def test_update_user_with_empty_password(self, logged_in_client, sample_users):
        """Test updating user with empty password"""
        user_id = sample_users[0]
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Password is required' in response.data
    
    def test_update_user_with_invalid_gender(self, logged_in_client, sample_users):
        """Test updating user with invalid gender"""
        user_id = sample_users[0]
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'gender': 'Other'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Gender must be one of' in response.data
    
    def test_update_user_with_duplicate_username(self, logged_in_client, sample_users):
        """Test updating user with another user's username"""
        user_id = sample_users[0]
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'user1',  # Another user's username
            'email': 'different@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Username already exists' in response.data
    
    def test_update_user_with_duplicate_email(self, logged_in_client, sample_users):
        """Test updating user with another user's email"""
        user_id = sample_users[0]
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'differentuser',
            'email': 'user1@example.com',  # Another user's email
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Email already registered' in response.data
    
    def test_update_user_password_is_hashed(self, logged_in_client, sample_users):
        """Test that updated user password is hashed with bcrypt"""
        user_id = sample_users[0]
        logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'updateduser',
            'email': 'updated@example.com',
            'password': 'newplainpassword',
            'gender': 'Male'
        }, follow_redirects=True)
        
        # Verify password is hashed
        with logged_in_client.application.app_context():
            user = User.query.get(user_id)
            assert user.password != 'newplainpassword'
            assert user.password.startswith('$2b$')  # Bcrypt hash format
            assert bcrypt.check_password_hash(user.password, 'newplainpassword')
    
    def test_update_user_can_keep_same_username(self, logged_in_client, sample_users):
        """Test updating user can keep the same username"""
        user_id = sample_users[0]
        
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'user0',  # Keep same username
            'email': 'newemail@example.com',
            'password': 'newpassword',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User updated successfully' in response.data
    
    def test_update_user_can_keep_same_email(self, logged_in_client, sample_users):
        """Test updating user can keep the same email"""
        user_id = sample_users[0]
        
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'newusername',
            'email': 'user0@example.com',  # Keep same email
            'password': 'newpassword',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User updated successfully' in response.data


class TestDeleteUserRoute:
    """Tests for delete_user route"""
    
    def test_delete_user_with_valid_id(self, logged_in_client, sample_users):
        """Test deleting user with valid ID"""
        user_id = sample_users[0]
        response = logged_in_client.get(f'/users/delete/{user_id}', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User deleted successfully' in response.data
        
        # Verify user was deleted from database
        with logged_in_client.application.app_context():
            user = User.query.get(user_id)
            assert user is None
    
    def test_delete_user_with_invalid_id(self, logged_in_client):
        """Test deleting user with invalid ID"""
        response = logged_in_client.get('/users/delete/invalid', follow_redirects=True)
        assert response.status_code == 200
        assert b'Invalid user ID' in response.data
    
    def test_delete_user_with_nonexistent_id(self, logged_in_client):
        """Test deleting user with non-existent ID"""
        response = logged_in_client.get('/users/delete/99999', follow_redirects=True)
        assert response.status_code == 200
        assert b'User not found' in response.data
    
    def test_delete_user_redirects_to_list(self, logged_in_client, sample_users):
        """Test delete user redirects to users list"""
        user_id = sample_users[0]
        response = logged_in_client.get(f'/users/delete/{user_id}', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'Users Management' in response.data


class TestUsersCRUDFlow:
    """Integration tests for complete CRUD flow"""
    
    def test_complete_crud_flow(self, logged_in_client):
        """Test complete CRUD flow: create -> read -> update -> delete"""
        # Create user
        response = logged_in_client.post('/users/create', data={
            'username': 'cruduser',
            'email': 'crud@example.com',
            'password': 'crudpassword',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User created successfully' in response.data
        
        # Read user (list)
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert b'cruduser' in response.data
        assert b'crud@example.com' in response.data
        
        # Get user ID
        with logged_in_client.application.app_context():
            user = User.query.filter_by(username='cruduser').first()
            user_id = user.id
        
        # Update user
        response = logged_in_client.post(f'/users/update/{user_id}', data={
            'username': 'cruduser_updated',
            'email': 'crud_updated@example.com',
            'password': 'newpassword',
            'gender': 'Female'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User updated successfully' in response.data
        
        # Verify update
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert b'cruduser_updated' in response.data
        assert b'crud_updated@example.com' in response.data
        
        # Delete user
        response = logged_in_client.get(f'/users/delete/{user_id}', follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User deleted successfully' in response.data
        
        # Verify deletion
        response = logged_in_client.get('/users/')
        assert response.status_code == 200
        assert b'cruduser_updated' not in response.data
    
    def test_sql_injection_attempts_are_treated_as_literal_strings(self, logged_in_client):
        """Test that SQL injection attempts are treated as literal strings"""
        # Attempt SQL injection in username
        response = logged_in_client.post('/users/create', data={
            'username': "admin' OR '1'='1",
            'email': 'injection@example.com',
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        assert b'User created successfully' in response.data
        
        # Verify the SQL injection string was stored as literal text
        with logged_in_client.application.app_context():
            user = User.query.filter_by(email='injection@example.com').first()
            assert user is not None
            assert user.username == "admin' OR '1'='1"
        
        # Attempt SQL injection in email
        response = logged_in_client.post('/users/create', data={
            'username': 'testuser2',
            'email': "test@example.com' UNION SELECT * FROM users--",
            'password': 'password123',
            'gender': 'Male'
        }, follow_redirects=True)
        
        # Should fail email validation, not SQL injection
        assert response.status_code == 200
        assert b'Invalid email format' in response.data
