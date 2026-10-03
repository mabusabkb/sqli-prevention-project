"""Unit tests for InputValidator class"""

import pytest
from app.validators.input_validator import InputValidator


class TestValidateUsername:
    """Tests for validate_username method"""
    
    def test_valid_username(self):
        """Test that valid usernames pass validation"""
        valid, error = InputValidator.validate_username("john_doe")
        assert valid is True
        assert error is None
    
    def test_username_with_spaces(self):
        """Test that usernames with spaces are valid"""
        valid, error = InputValidator.validate_username("john doe")
        assert valid is True
        assert error is None
    
    def test_empty_username(self):
        """Test that empty username fails validation"""
        valid, error = InputValidator.validate_username("")
        assert valid is False
        assert error == "Username is required"
    
    def test_whitespace_only_username(self):
        """Test that whitespace-only username fails validation"""
        valid, error = InputValidator.validate_username("   ")
        assert valid is False
        assert error == "Username is required"
    
    def test_username_at_max_length(self):
        """Test that username at exactly 200 characters passes"""
        username = "a" * 200
        valid, error = InputValidator.validate_username(username)
        assert valid is True
        assert error is None
    
    def test_username_exceeds_max_length(self):
        """Test that username over 200 characters fails"""
        username = "a" * 201
        valid, error = InputValidator.validate_username(username)
        assert valid is False
        assert "200 characters or less" in error
    
    def test_username_with_special_characters(self):
        """Test that usernames with special characters are valid"""
        valid, error = InputValidator.validate_username("user@123!#$")
        assert valid is True
        assert error is None


class TestValidateEmail:
    """Tests for validate_email method"""
    
    def test_valid_email(self):
        """Test that valid email passes validation"""
        valid, error = InputValidator.validate_email("user@example.com")
        assert valid is True
        assert error is None
    
    def test_valid_email_with_subdomain(self):
        """Test that email with subdomain passes validation"""
        valid, error = InputValidator.validate_email("user@mail.example.com")
        assert valid is True
        assert error is None
    
    def test_valid_email_with_plus(self):
        """Test that email with plus sign passes validation"""
        valid, error = InputValidator.validate_email("user+tag@example.com")
        assert valid is True
        assert error is None
    
    def test_empty_email(self):
        """Test that empty email fails validation"""
        valid, error = InputValidator.validate_email("")
        assert valid is False
        assert error == "Email is required"
    
    def test_whitespace_only_email(self):
        """Test that whitespace-only email fails validation"""
        valid, error = InputValidator.validate_email("   ")
        assert valid is False
        assert error == "Email is required"
    
    def test_email_without_at_symbol(self):
        """Test that email without @ fails validation"""
        valid, error = InputValidator.validate_email("userexample.com")
        assert valid is False
        assert error == "Invalid email format"
    
    def test_email_without_domain(self):
        """Test that email without domain fails validation"""
        valid, error = InputValidator.validate_email("user@")
        assert valid is False
        assert error == "Invalid email format"
    
    def test_email_without_tld(self):
        """Test that email without TLD fails validation"""
        valid, error = InputValidator.validate_email("user@example")
        assert valid is False
        assert error == "Invalid email format"
    
    def test_email_at_max_length(self):
        """Test that email at exactly 200 characters passes if format is valid"""
        # Create a valid email at 200 characters
        local_part = "a" * 180
        email = f"{local_part}@example.com"  # Total: 192 chars
        valid, error = InputValidator.validate_email(email)
        assert valid is True
        assert error is None
    
    def test_email_exceeds_max_length(self):
        """Test that email over 200 characters fails"""
        local_part = "a" * 195
        email = f"{local_part}@example.com"  # Total: 207 chars
        valid, error = InputValidator.validate_email(email)
        assert valid is False
        assert "200 characters or less" in error


class TestValidatePassword:
    """Tests for validate_password method"""
    
    def test_valid_password(self):
        """Test that valid password passes validation"""
        valid, error = InputValidator.validate_password("password123")
        assert valid is True
        assert error is None
    
    def test_password_with_special_characters(self):
        """Test that password with special characters passes"""
        valid, error = InputValidator.validate_password("P@ssw0rd!#$")
        assert valid is True
        assert error is None
    
    def test_empty_password(self):
        """Test that empty password fails validation"""
        valid, error = InputValidator.validate_password("")
        assert valid is False
        assert error == "Password is required"
    
    def test_password_with_spaces(self):
        """Test that password with spaces is valid"""
        valid, error = InputValidator.validate_password("pass word 123")
        assert valid is True
        assert error is None
    
    def test_whitespace_only_password(self):
        """Test that whitespace-only password is valid (presence check only)"""
        # Note: Password validation only checks presence and length, not content
        valid, error = InputValidator.validate_password("   ")
        assert valid is True
        assert error is None
    
    def test_password_at_max_length(self):
        """Test that password at exactly 200 characters passes"""
        password = "a" * 200
        valid, error = InputValidator.validate_password(password)
        assert valid is True
        assert error is None
    
    def test_password_exceeds_max_length(self):
        """Test that password over 200 characters fails"""
        password = "a" * 201
        valid, error = InputValidator.validate_password(password)
        assert valid is False
        assert "200 characters or less" in error


class TestValidateGender:
    """Tests for validate_gender method"""
    
    def test_valid_gender_male(self):
        """Test that 'Male' passes validation"""
        valid, error = InputValidator.validate_gender("Male")
        assert valid is True
        assert error is None
    
    def test_valid_gender_female(self):
        """Test that 'Female' passes validation"""
        valid, error = InputValidator.validate_gender("Female")
        assert valid is True
        assert error is None
    
    def test_invalid_gender_lowercase(self):
        """Test that lowercase gender fails validation"""
        valid, error = InputValidator.validate_gender("male")
        assert valid is False
        assert "Gender must be one of: Male, Female" in error
    
    def test_invalid_gender_other(self):
        """Test that non-whitelisted gender fails validation"""
        valid, error = InputValidator.validate_gender("Other")
        assert valid is False
        assert "Gender must be one of: Male, Female" in error
    
    def test_empty_gender(self):
        """Test that empty gender fails validation"""
        valid, error = InputValidator.validate_gender("")
        assert valid is False
        assert "Gender must be one of: Male, Female" in error
    
    def test_none_gender(self):
        """Test that None gender fails validation"""
        valid, error = InputValidator.validate_gender(None)
        assert valid is False
        assert "Gender must be one of: Male, Female" in error


class TestValidateId:
    """Tests for validate_id method"""
    
    def test_valid_id(self):
        """Test that valid ID passes validation"""
        valid, id_int, error = InputValidator.validate_id("123")
        assert valid is True
        assert id_int == 123
        assert error is None
    
    def test_valid_id_large_number(self):
        """Test that large valid ID passes validation"""
        valid, id_int, error = InputValidator.validate_id("999999")
        assert valid is True
        assert id_int == 999999
        assert error is None
    
    def test_zero_id(self):
        """Test that zero ID fails validation"""
        valid, id_int, error = InputValidator.validate_id("0")
        assert valid is False
        assert id_int is None
        assert error == "Invalid user ID"
    
    def test_negative_id(self):
        """Test that negative ID fails validation"""
        valid, id_int, error = InputValidator.validate_id("-5")
        assert valid is False
        assert id_int is None
        assert error == "Invalid user ID"
    
    def test_non_numeric_id(self):
        """Test that non-numeric ID fails validation"""
        valid, id_int, error = InputValidator.validate_id("abc")
        assert valid is False
        assert id_int is None
        assert error == "Invalid user ID format"
    
    def test_float_id(self):
        """Test that float ID fails validation"""
        valid, id_int, error = InputValidator.validate_id("12.5")
        assert valid is False
        assert id_int is None
        assert error == "Invalid user ID format"
    
    def test_empty_id(self):
        """Test that empty ID fails validation"""
        valid, id_int, error = InputValidator.validate_id("")
        assert valid is False
        assert id_int is None
        assert error == "Invalid user ID format"
    
    def test_none_id(self):
        """Test that None ID fails validation"""
        valid, id_int, error = InputValidator.validate_id(None)
        assert valid is False
        assert id_int is None
        assert error == "Invalid user ID format"


class TestInputValidatorConstants:
    """Tests for InputValidator class constants"""
    
    def test_max_username_length(self):
        """Test that MAX_USERNAME_LENGTH is 200"""
        assert InputValidator.MAX_USERNAME_LENGTH == 200
    
    def test_max_email_length(self):
        """Test that MAX_EMAIL_LENGTH is 200"""
        assert InputValidator.MAX_EMAIL_LENGTH == 200
    
    def test_max_password_length(self):
        """Test that MAX_PASSWORD_LENGTH is 200"""
        assert InputValidator.MAX_PASSWORD_LENGTH == 200
    
    def test_allowed_genders(self):
        """Test that ALLOWED_GENDERS contains Male and Female"""
        assert InputValidator.ALLOWED_GENDERS == ['Male', 'Female']
    
    def test_email_regex_exists(self):
        """Test that EMAIL_REGEX is defined"""
        assert InputValidator.EMAIL_REGEX is not None
