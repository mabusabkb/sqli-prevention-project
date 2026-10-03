"""Input validation module for user inputs"""

import re
from typing import Tuple, Optional


class InputValidator:
    """
    Validates and sanitizes user inputs to prevent injection attacks.
    All validation methods return (is_valid, error_message) tuples.
    """
    
    # Email validation regex pattern
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    # Maximum length constraints
    MAX_USERNAME_LENGTH = 200
    MAX_EMAIL_LENGTH = 200
    MAX_PASSWORD_LENGTH = 200
    
    # Allowed gender values
    ALLOWED_GENDERS = ['Male', 'Female']
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """
        Validates username with presence and length checks.
        
        Args:
            username: The username string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: None if valid, descriptive error message if invalid
        """
        if not username or not username.strip():
            return False, "Username is required"
        
        if len(username) > InputValidator.MAX_USERNAME_LENGTH:
            return False, f"Username must be {InputValidator.MAX_USERNAME_LENGTH} characters or less"
        
        return True, None
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, Optional[str]]:
        """
        Validates email with regex pattern and length checks.
        
        Args:
            email: The email string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: None if valid, descriptive error message if invalid
        """
        if not email or not email.strip():
            return False, "Email is required"
        
        if len(email) > InputValidator.MAX_EMAIL_LENGTH:
            return False, f"Email must be {InputValidator.MAX_EMAIL_LENGTH} characters or less"
        
        if not InputValidator.EMAIL_REGEX.match(email):
            return False, "Invalid email format"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validates password with presence and length checks.
        
        Args:
            password: The password string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: None if valid, descriptive error message if invalid
        """
        if not password:
            return False, "Password is required"
        
        if len(password) > InputValidator.MAX_PASSWORD_LENGTH:
            return False, f"Password must be {InputValidator.MAX_PASSWORD_LENGTH} characters or less"
        
        return True, None
    
    @staticmethod
    def validate_gender(gender: str) -> Tuple[bool, Optional[str]]:
        """
        Validates gender with whitelist validation.
        
        Args:
            gender: The gender string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
            - is_valid: True if validation passes, False otherwise
            - error_message: None if valid, descriptive error message if invalid
        """
        if not gender or gender not in InputValidator.ALLOWED_GENDERS:
            return False, f"Gender must be one of: {', '.join(InputValidator.ALLOWED_GENDERS)}"
        
        return True, None
    
    @staticmethod
    def validate_id(user_id: str) -> Tuple[bool, Optional[int], Optional[str]]:
        """
        Validates and converts user ID with type conversion and range validation.
        
        Args:
            user_id: The user ID string to validate and convert
            
        Returns:
            Tuple of (is_valid, converted_id, error_message)
            - is_valid: True if validation passes, False otherwise
            - converted_id: Integer ID if valid, None if invalid
            - error_message: None if valid, descriptive error message if invalid
        """
        try:
            id_int = int(user_id)
            if id_int <= 0:
                return False, None, "Invalid user ID"
            return True, id_int, None
        except (ValueError, TypeError):
            return False, None, "Invalid user ID format"
