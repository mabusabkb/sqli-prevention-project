"""
User management service for CRUD operations.
Implements secure user management with SQLAlchemy ORM and bcrypt password hashing.
"""
import logging
from typing import List, Optional, Tuple
from app import db, bcrypt
from app.models.user import User


class UserService:
    """
    Handles user management business logic.
    
    This service provides CRUD operations for user management with:
    - SQLAlchemy ORM for SQL injection prevention
    - Bcrypt password hashing (cost factor 12)
    - Comprehensive error handling with secure logging
    - Generic error messages to prevent information disclosure
    """
    
    @staticmethod
    def get_all_users() -> Tuple[bool, Optional[List[User]], Optional[str]]:
        """
        Retrieve all users from the database.
        
        This method uses SQLAlchemy ORM which automatically generates
        parameterized queries to prevent SQL injection.
        
        Returns:
            Tuple of (success: bool, users: Optional[List[User]], error_message: Optional[str])
            - (True, [user_objects], None) on success
            - (False, None, error_message) on failure
        
        Security Features:
            - SQLAlchemy ORM prevents SQL injection
            - Secure error logging without exposing details to users
            - Generic error messages prevent information disclosure
        
        Example:
            >>> success, users, error = UserService.get_all_users()
            >>> if success:
            ...     for user in users:
            ...         print(user.username)
        """
        try:
            # Query all users using SQLAlchemy ORM
            # SQLAlchemy automatically uses parameterized queries
            users = User.query.all()
            
            # Log success
            logging.info(f"Retrieved {len(users)} users from database")
            
            return True, users, None
            
        except Exception as e:
            # Log error securely with full details
            logging.error(f"Error fetching all users: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Return generic error message to user
            # Never expose database schema, queries, or internal details
            return False, None, "An error occurred while retrieving users"
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Retrieve a user by their ID.
        
        This method uses SQLAlchemy ORM which automatically generates
        parameterized queries to prevent SQL injection.
        
        Args:
            user_id: The ID of the user to retrieve
        
        Returns:
            Tuple of (success: bool, user: Optional[User], error_message: Optional[str])
            - (True, user_object, None) on success
            - (False, None, error_message) if user not found or on error
        
        Security Features:
            - SQLAlchemy ORM prevents SQL injection
            - Secure error logging without exposing details to users
            - Generic error messages prevent information disclosure
        
        Example:
            >>> success, user, error = UserService.get_user_by_id(1)
            >>> if success:
            ...     print(f"Found user: {user.username}")
        """
        try:
            # Query user by ID using SQLAlchemy ORM
            # SQLAlchemy.query.get() uses parameterized queries
            user = User.query.get(user_id)
            
            if not user:
                # User not found
                logging.warning(f"User with ID {user_id} not found")
                return False, None, "User not found"
            
            # Log success
            logging.info(f"Retrieved user: {user.username} (ID: {user_id})")
            
            return True, user, None
            
        except Exception as e:
            # Log error securely with full details
            logging.error(f"Error fetching user with ID {user_id}: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Return generic error message to user
            # Never expose database schema, queries, or internal details
            return False, None, "An error occurred while retrieving the user"
    
    @staticmethod
    def create_user(
        username: str,
        email: str,
        password: str,
        gender: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Create a new user with secure password hashing.
        
        This method:
        - Checks for duplicate username/email
        - Hashes password with bcrypt (cost factor 12)
        - Creates user record using SQLAlchemy ORM (prevents SQL injection)
        - Returns generic error messages to prevent information disclosure
        
        Args:
            username: User's username
            email: User's email address
            password: User's plain text password (will be hashed)
            gender: User's gender (Male or Female)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
            - (True, None) on success
            - (False, error_message) on failure
        
        Security Features:
            - Bcrypt password hashing with cost factor 12
            - SQLAlchemy ORM prevents SQL injection
            - Duplicate checking prevents data integrity issues
            - Secure error logging without exposing details to users
        
        Example:
            >>> success, error = UserService.create_user("john", "john@example.com", "pass123", "Male")
            >>> if success:
            ...     print("User created successfully")
        """
        try:
            # Check if username already exists
            # SQLAlchemy uses parameterized queries - prevents SQL injection
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                logging.warning(f"Attempt to create user with duplicate username: {username}")
                return False, "Username already exists"
            
            # Check if email already exists
            # SQLAlchemy uses parameterized queries - prevents SQL injection
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                logging.warning(f"Attempt to create user with duplicate email: {email}")
                return False, "Email already registered"
            
            # Hash password with bcrypt (cost factor 12)
            # Cost factor 12 = 2^12 = 4096 iterations
            # Provides strong security while maintaining reasonable performance
            hashed_password = bcrypt.generate_password_hash(
                password,
                rounds=12
            ).decode('utf-8')
            
            # Create new user
            # SQLAlchemy ORM handles parameterization automatically
            new_user = User(
                username=username,
                email=email,
                password=hashed_password,
                gender=gender
            )
            
            # Add to database
            db.session.add(new_user)
            db.session.commit()
            
            # Log success (without sensitive data)
            logging.info(f"User created successfully: {username}")
            
            return True, None
            
        except Exception as e:
            # Rollback transaction on error
            db.session.rollback()
            
            # Log error securely with full details
            logging.error(f"Error creating user '{username}': {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Return generic error message to user
            # Never expose database schema, queries, or internal details
            return False, "An error occurred while creating the user"
    
    @staticmethod
    def update_user(
        user_id: int,
        username: str,
        email: str,
        password: str,
        gender: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Update an existing user.
        
        This method:
        - Retrieves user by ID using SQLAlchemy ORM
        - Checks for duplicate username/email (excluding current user)
        - Hashes new password with bcrypt (cost factor 12)
        - Updates user record using SQLAlchemy ORM (prevents SQL injection)
        - Returns generic error messages to prevent information disclosure
        
        Args:
            user_id: ID of the user to update
            username: New username
            email: New email address
            password: New plain text password (will be hashed)
            gender: New gender (Male or Female)
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
            - (True, None) on success
            - (False, error_message) on failure
        
        Security Features:
            - SQLAlchemy ORM prevents SQL injection
            - Bcrypt password hashing with cost factor 12
            - Duplicate checking prevents data integrity issues
            - Secure error logging without exposing details to users
        
        Example:
            >>> success, error = UserService.update_user(1, "john_updated", "john@example.com", "newpass", "Male")
            >>> if success:
            ...     print("User updated successfully")
        """
        try:
            # Query user by ID using SQLAlchemy ORM
            # SQLAlchemy.query.get() uses parameterized queries
            user = User.query.get(user_id)
            
            if not user:
                # User not found
                logging.warning(f"Attempt to update non-existent user with ID: {user_id}")
                return False, "User not found"
            
            # Check if new username already exists (excluding current user)
            # SQLAlchemy uses parameterized queries - prevents SQL injection
            if username != user.username:
                existing_user = User.query.filter_by(username=username).first()
                if existing_user:
                    logging.warning(f"Attempt to update user {user_id} with duplicate username: {username}")
                    return False, "Username already exists"
            
            # Check if new email already exists (excluding current user)
            # SQLAlchemy uses parameterized queries - prevents SQL injection
            if email != user.email:
                existing_email = User.query.filter_by(email=email).first()
                if existing_email:
                    logging.warning(f"Attempt to update user {user_id} with duplicate email: {email}")
                    return False, "Email already registered"
            
            # Hash new password with bcrypt (cost factor 12)
            hashed_password = bcrypt.generate_password_hash(
                password,
                rounds=12
            ).decode('utf-8')
            
            # Update user fields
            # SQLAlchemy ORM handles parameterization automatically
            user.username = username
            user.email = email
            user.password = hashed_password
            user.gender = gender
            
            # Commit changes to database
            db.session.commit()
            
            # Log success (without sensitive data)
            logging.info(f"User updated successfully: {username} (ID: {user_id})")
            
            return True, None
            
        except Exception as e:
            # Rollback transaction on error
            db.session.rollback()
            
            # Log error securely with full details
            logging.error(f"Error updating user with ID {user_id}: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Return generic error message to user
            # Never expose database schema, queries, or internal details
            return False, "An error occurred while updating the user"
    
    @staticmethod
    def delete_user(user_id: int) -> Tuple[bool, Optional[str]]:
        """
        Delete a user by their ID.
        
        This method:
        - Retrieves user by ID using SQLAlchemy ORM
        - Checks if user exists before deletion
        - Deletes user record using SQLAlchemy ORM (prevents SQL injection)
        - Returns generic error messages to prevent information disclosure
        
        Args:
            user_id: ID of the user to delete
        
        Returns:
            Tuple of (success: bool, error_message: Optional[str])
            - (True, None) on success
            - (False, error_message) on failure
        
        Security Features:
            - SQLAlchemy ORM prevents SQL injection
            - Existence checking prevents errors
            - Secure error logging without exposing details to users
        
        Example:
            >>> success, error = UserService.delete_user(1)
            >>> if success:
            ...     print("User deleted successfully")
        """
        try:
            # Query user by ID using SQLAlchemy ORM
            # SQLAlchemy.query.get() uses parameterized queries
            user = User.query.get(user_id)
            
            if not user:
                # User not found
                logging.warning(f"Attempt to delete non-existent user with ID: {user_id}")
                return False, "User not found"
            
            # Store username for logging before deletion
            username = user.username
            
            # Delete user
            # SQLAlchemy ORM handles parameterization automatically
            db.session.delete(user)
            db.session.commit()
            
            # Log success
            logging.info(f"User deleted successfully: {username} (ID: {user_id})")
            
            return True, None
            
        except Exception as e:
            # Rollback transaction on error
            db.session.rollback()
            
            # Log error securely with full details
            logging.error(f"Error deleting user with ID {user_id}: {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Return generic error message to user
            # Never expose database schema, queries, or internal details
            return False, "An error occurred while deleting the user"
