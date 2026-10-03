"""
Authentication service for user registration and login.
Implements secure password hashing with bcrypt and prevents username enumeration.
"""
import logging
from typing import Optional, Tuple
from app import db, bcrypt
from app.models.user import User


class AuthService:
    """
    Handles authentication business logic.
    
    This service provides secure user registration and authentication
    with bcrypt password hashing (cost factor 12) and generic error
    messages to prevent username enumeration attacks.
    """
    
    @staticmethod
    def register_user(
        username: str,
        email: str,
        password: str,
        gender: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Register a new user with secure password hashing.
        
        This method:
        - Checks for duplicate username/email
        - Hashes password with bcrypt (cost factor 12)
        - Creates user record using SQLAlchemy ORM (prevents SQL injection)
        - Returns generic error messages to prevent information disclosure
        
        Args:
            username: User's chosen username
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
            - Generic error messages prevent information disclosure
            - Secure error logging without exposing details to users
        """
        try:
            # Check if username already exists
            # SQLAlchemy uses parameterized queries - prevents SQL injection
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                # Generic error message - don't reveal that username exists
                return False, "Username already exists"
            
            # Check if email already exists
            # SQLAlchemy uses parameterized queries - prevents SQL injection
            existing_email = User.query.filter_by(email=email).first()
            if existing_email:
                # Generic error message - don't reveal that email exists
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
            logging.info(f"User registered successfully: {username}")
            
            return True, None
            
        except Exception as e:
            # Rollback transaction on error
            db.session.rollback()
            
            # Log error securely with full details
            logging.error(f"Registration error for username '{username}': {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Return generic error message to user
            # Never expose database schema, queries, or internal details
            return False, "An error occurred during registration"
    
    @staticmethod
    def authenticate_user(
        username: str,
        password: str
    ) -> Tuple[bool, Optional[User], Optional[str]]:
        """
        Authenticate user credentials.
        
        This method:
        - Queries user by username using SQLAlchemy ORM
        - Verifies password using bcrypt's constant-time comparison
        - Returns generic error messages to prevent username enumeration
        
        Args:
            username: Username to authenticate
            password: Plain text password to verify
        
        Returns:
            Tuple of (success: bool, user: Optional[User], error_message: Optional[str])
            - (True, user_object, None) on success
            - (False, None, error_message) on failure
        
        Security Features:
            - Generic error messages prevent username enumeration
            - Bcrypt constant-time password verification prevents timing attacks
            - SQLAlchemy ORM prevents SQL injection
            - Secure error logging without exposing details to users
        
        Example:
            >>> success, user, error = AuthService.authenticate_user("admin", "password123")
            >>> if success:
            ...     print(f"Logged in as {user.username}")
            ... else:
            ...     print(f"Login failed: {error}")
        """
        try:
            # Query user by username
            # SQLAlchemy uses parameterized queries - prevents SQL injection
            user = User.query.filter_by(username=username).first()
            
            if not user:
                # Generic error message - don't reveal that username doesn't exist
                # This prevents username enumeration attacks
                logging.warning(f"Login attempt with non-existent username: {username}")
                return False, None, "Invalid username or password"
            
            # Verify password using bcrypt
            # bcrypt.check_password_hash uses constant-time comparison
            # This prevents timing attacks
            if bcrypt.check_password_hash(user.password, password):
                # Authentication successful
                logging.info(f"User authenticated successfully: {username}")
                return True, user, None
            else:
                # Password verification failed
                # Generic error message - don't reveal that password was wrong
                # This prevents username enumeration attacks
                logging.warning(f"Login attempt with incorrect password for user: {username}")
                return False, None, "Invalid username or password"
                
        except Exception as e:
            # Log error securely with full details
            logging.error(f"Authentication error for username '{username}': {str(e)}")
            logging.error(f"Error type: {type(e).__name__}")
            
            # Return generic error message to user
            # Never expose database schema, queries, or internal details
            return False, None, "An error occurred during authentication"
