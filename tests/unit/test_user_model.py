"""
Unit tests for the User model.
Tests model creation, validation, and methods.
"""
import pytest
from datetime import datetime
from app.models.user import User
from app import db


class TestUserModel:
    """Test suite for User model"""
    
    def test_user_creation(self, app, db):
        """Test creating a user with all required fields"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='hashed_password_here',
                gender='Male'
            )
            db.session.add(user)
            db.session.commit()
            
            # Verify user was created
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.email == 'test@example.com'
            assert user.password == 'hashed_password_here'
            assert user.gender == 'Male'
            assert user.created_at is not None
            assert isinstance(user.created_at, datetime)
    
    def test_user_repr(self, app):
        """Test __repr__ method returns correct string"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='hashed_password',
                gender='Female'
            )
            
            assert repr(user) == '<User testuser>'
    
    def test_user_to_dict_excludes_password(self, app):
        """Test to_dict() method excludes password field"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='secret_password',
                gender='Male'
            )
            db.session.add(user)
            db.session.commit()
            
            user_dict = user.to_dict()
            
            # Verify password is not in dictionary
            assert 'password' not in user_dict
            
            # Verify other fields are present
            assert user_dict['id'] == user.id
            assert user_dict['username'] == 'testuser'
            assert user_dict['email'] == 'test@example.com'
            assert user_dict['gender'] == 'Male'
            assert user_dict['created_at'] is not None
    
    def test_username_unique_constraint(self, app):
        """Test that duplicate usernames are rejected"""
        with app.app_context():
            user1 = User(
                username='duplicate',
                email='user1@example.com',
                password='password1',
                gender='Male'
            )
            db.session.add(user1)
            db.session.commit()
            
            # Try to create another user with same username
            user2 = User(
                username='duplicate',
                email='user2@example.com',
                password='password2',
                gender='Female'
            )
            db.session.add(user2)
            
            # Should raise IntegrityError
            with pytest.raises(Exception):  # SQLAlchemy raises IntegrityError
                db.session.commit()
            
            db.session.rollback()
    
    def test_email_unique_constraint(self, app):
        """Test that duplicate emails are rejected"""
        with app.app_context():
            user1 = User(
                username='user1',
                email='duplicate@example.com',
                password='password1',
                gender='Male'
            )
            db.session.add(user1)
            db.session.commit()
            
            # Try to create another user with same email
            user2 = User(
                username='user2',
                email='duplicate@example.com',
                password='password2',
                gender='Female'
            )
            db.session.add(user2)
            
            # Should raise IntegrityError
            with pytest.raises(Exception):
                db.session.commit()
            
            db.session.rollback()
    
    def test_gender_check_constraint_male(self, app):
        """Test that Male gender is accepted"""
        with app.app_context():
            user = User(
                username='maleuser',
                email='male@example.com',
                password='password',
                gender='Male'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.gender == 'Male'
    
    def test_gender_check_constraint_female(self, app):
        """Test that Female gender is accepted"""
        with app.app_context():
            user = User(
                username='femaleuser',
                email='female@example.com',
                password='password',
                gender='Female'
            )
            db.session.add(user)
            db.session.commit()
            
            assert user.gender == 'Female'
    
    def test_gender_check_constraint_invalid(self, app):
        """Test that invalid gender values are rejected by check constraint"""
        with app.app_context():
            user = User(
                username='invaliduser',
                email='invalid@example.com',
                password='password',
                gender='Other'  # Invalid value
            )
            db.session.add(user)
            
            # Should raise IntegrityError due to check constraint
            with pytest.raises(Exception):
                db.session.commit()
            
            db.session.rollback()
    
    def test_created_at_auto_set(self, app):
        """Test that created_at is automatically set on creation"""
        with app.app_context():
            before_creation = datetime.utcnow()
            
            user = User(
                username='timetest',
                email='time@example.com',
                password='password',
                gender='Male'
            )
            db.session.add(user)
            db.session.commit()
            
            after_creation = datetime.utcnow()
            
            # Verify created_at is set and within expected range
            assert user.created_at is not None
            assert before_creation <= user.created_at <= after_creation
    
    def test_id_auto_increment(self, app):
        """Test that id is auto-incremented"""
        with app.app_context():
            user1 = User(
                username='user1',
                email='user1@example.com',
                password='password1',
                gender='Male'
            )
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(
                username='user2',
                email='user2@example.com',
                password='password2',
                gender='Female'
            )
            db.session.add(user2)
            db.session.commit()
            
            # Verify IDs are auto-incremented
            assert user1.id is not None
            assert user2.id is not None
            assert user2.id > user1.id
    
    def test_to_dict_with_created_at_none(self, app):
        """Test to_dict() handles None created_at gracefully"""
        with app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                password='password',
                gender='Male'
            )
            # Don't commit, so created_at might be None in some edge cases
            user.created_at = None
            
            user_dict = user.to_dict()
            
            # Should handle None gracefully
            assert user_dict['created_at'] is None
