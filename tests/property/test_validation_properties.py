"""
Property-based tests for input validation.
Tests length constraints, whitespace rejection, gender whitelist, and email validation.
"""
import pytest
from hypothesis import given, strategies as st, settings, assume
from app.validators.input_validator import InputValidator


class TestInputValidationProperties:
    """Property tests for input validation"""
    
    @settings(max_examples=100)
    @given(text=st.text(min_size=0, max_size=200))
    def test_length_constraint_username_at_or_below_200(self, text):
        """
        Property: Strings <= 200 characters pass username validation.
        Validates: Requirements 3.3
        """
        valid, error = InputValidator.validate_username(text)
        
        # If validation fails, it should not be due to length
        if not valid and error:
            assert "200 characters" not in error or len(text) == 0 or not text.strip()
    
    @settings(max_examples=100)
    @given(text=st.text(min_size=201, max_size=500))
    def test_length_constraint_username_above_200_fails(self, text):
        """
        Property: Strings > 200 characters fail username validation.
        Validates: Requirements 3.3
        """
        valid, error = InputValidator.validate_username(text)
        
        # Should fail due to length
        assert valid is False
        assert error is not None
        assert "200 characters" in error
    
    @settings(max_examples=100)
    @given(text=st.text(min_size=0, max_size=200))
    def test_length_constraint_email_at_or_below_200(self, text):
        """
        Property: Strings <= 200 characters pass email length check.
        Validates: Requirements 3.5
        """
        valid, error = InputValidator.validate_email(text)
        
        # If validation fails, check it's not due to length (may be format)
        if not valid and error and len(text) <= 200:
            assert "200 characters" not in error
    
    @settings(max_examples=100)
    @given(text=st.text(min_size=201, max_size=500))
    def test_length_constraint_email_above_200_fails(self, text):
        """
        Property: Strings > 200 characters fail email validation.
        Validates: Requirements 3.5
        """
        valid, error = InputValidator.validate_email(text)
        
        # Should fail due to length
        assert valid is False
        assert error is not None
        assert "200 characters" in error
    
    @settings(max_examples=100)
    @given(text=st.text(min_size=0, max_size=200))
    def test_length_constraint_password_at_or_below_200(self, text):
        """
        Property: Strings <= 200 characters pass password length check.
        Validates: Requirements 3.4
        """
        valid, error = InputValidator.validate_password(text)
        
        # If validation fails, it should not be due to length
        if not valid and error:
            assert "200 characters" not in error or len(text) == 0
    
    @settings(max_examples=100)
    @given(text=st.text(min_size=201, max_size=500))
    def test_length_constraint_password_above_200_fails(self, text):
        """
        Property: Strings > 200 characters fail password validation.
        Validates: Requirements 3.4
        """
        valid, error = InputValidator.validate_password(text)
        
        # Should fail due to length
        assert valid is False
        assert error is not None
        assert "200 characters" in error
    
    @settings(max_examples=100)
    @given(whitespace=st.text(alphabet=' \t\n\r\f\v', min_size=1, max_size=50))
    def test_whitespace_only_username_rejected(self, whitespace):
        """
        Property: Strings composed entirely of whitespace are rejected for username.
        Validates: Requirements 3.6
        """
        valid, error = InputValidator.validate_username(whitespace)
        
        # Should fail
        assert valid is False
        assert error is not None
        assert "required" in error.lower()
    
    @settings(max_examples=100)
    @given(whitespace=st.text(alphabet=' \t\n\r\f\v', min_size=1, max_size=50))
    def test_whitespace_only_email_rejected(self, whitespace):
        """
        Property: Strings composed entirely of whitespace are rejected for email.
        Validates: Requirements 3.6
        """
        valid, error = InputValidator.validate_email(whitespace)
        
        # Should fail
        assert valid is False
        assert error is not None
        assert "required" in error.lower() or "invalid" in error.lower()
    
    @settings(max_examples=100)
    @given(gender=st.text(min_size=1, max_size=50))
    def test_gender_whitelist_validation(self, gender):
        """
        Property: Only 'Male' and 'Female' pass gender validation.
        Validates: Requirements 3.8
        """
        valid, error = InputValidator.validate_gender(gender)
        
        if gender in ['Male', 'Female']:
            # Should pass
            assert valid is True
            assert error is None
        else:
            # Should fail
            assert valid is False
            assert error is not None
            assert "Male" in error and "Female" in error
    
    def test_gender_whitelist_only_male_and_female(self):
        """
        Test that only 'Male' and 'Female' are accepted.
        Validates: Requirements 3.8
        """
        # Valid values
        valid, error = InputValidator.validate_gender("Male")
        assert valid is True
        assert error is None
        
        valid, error = InputValidator.validate_gender("Female")
        assert valid is True
        assert error is None
        
        # Invalid values
        invalid_genders = ["male", "female", "MALE", "FEMALE", "Other", "Non-binary", "", "M", "F"]
        for gender in invalid_genders:
            valid, error = InputValidator.validate_gender(gender)
            assert valid is False, f"Gender '{gender}' should be invalid"
            assert error is not None
    
    @settings(max_examples=100)
    @given(
        local=st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789._-', min_size=1, max_size=20),
        domain=st.text(alphabet='abcdefghijklmnopqrstuvwxyz0123456789-', min_size=1, max_size=20),
        tld=st.text(alphabet='abcdefghijklmnopqrstuvwxyz', min_size=2, max_size=10)
    )
    def test_valid_email_format_passes(self, local, domain, tld):
        """
        Property: Valid email formats pass validation.
        Validates: Requirements 3.2, 3.7
        """
        # Construct valid email
        email = f"{local}@{domain}.{tld}"
        
        # Skip if too long
        if len(email) > 200:
            return
        
        # Skip if domain or local starts/ends with invalid chars
        if local.startswith('.') or local.endswith('.'):
            return
        if domain.startswith('-') or domain.endswith('-'):
            return
        
        valid, error = InputValidator.validate_email(email)
        
        # Should pass
        assert valid is True, f"Valid email rejected: {email}, error: {error}"
        assert error is None
    
    @settings(max_examples=100)
    @given(text=st.text(min_size=1, max_size=50))
    def test_invalid_email_format_fails(self, text):
        """
        Property: Invalid email formats fail with descriptive error.
        Validates: Requirements 3.2, 3.7
        """
        # Skip if it happens to be a valid email format
        if '@' in text and '.' in text.split('@')[-1]:
            parts = text.split('@')
            if len(parts) == 2 and len(parts[1].split('.')) >= 2:
                return
        
        valid, error = InputValidator.validate_email(text)
        
        # Should fail
        assert valid is False
        assert error is not None
        assert "email" in error.lower() or "invalid" in error.lower() or "required" in error.lower()
    
    def test_empty_string_validation(self):
        """
        Test that empty strings are rejected for all fields.
        Validates: Requirements 3.1
        """
        # Username
        valid, error = InputValidator.validate_username("")
        assert valid is False
        assert "required" in error.lower()
        
        # Email
        valid, error = InputValidator.validate_email("")
        assert valid is False
        assert "required" in error.lower()
        
        # Password
        valid, error = InputValidator.validate_password("")
        assert valid is False
        assert "required" in error.lower()
        
        # Gender
        valid, error = InputValidator.validate_gender("")
        assert valid is False
    
    def test_boundary_conditions_exactly_200_characters(self):
        """
        Test boundary condition: exactly 200 characters.
        Validates: Requirements 3.3, 3.4, 3.5
        """
        text_200 = "a" * 200
        
        # Username - should pass
        valid, error = InputValidator.validate_username(text_200)
        assert valid is True
        
        # Password - should pass
        valid, error = InputValidator.validate_password(text_200)
        assert valid is True
        
        # Email (not valid format but should pass length check)
        # We check that length is not the reason for failure
        valid, error = InputValidator.validate_email(text_200)
        if not valid:
            assert "200 characters" not in error
    
    def test_boundary_conditions_201_characters(self):
        """
        Test boundary condition: 201 characters.
        Validates: Requirements 3.3, 3.4, 3.5
        """
        text_201 = "a" * 201
        
        # Username - should fail
        valid, error = InputValidator.validate_username(text_201)
        assert valid is False
        assert "200 characters" in error
        
        # Password - should fail
        valid, error = InputValidator.validate_password(text_201)
        assert valid is False
        assert "200 characters" in error
        
        # Email - should fail
        valid, error = InputValidator.validate_email(text_201)
        assert valid is False
        assert "200 characters" in error
    
    @settings(max_examples=100)
    @given(
        valid_text=st.text(min_size=1, max_size=50).filter(lambda x: x.strip()),
        whitespace_prefix=st.text(alphabet=' \t', min_size=1, max_size=10),
        whitespace_suffix=st.text(alphabet=' \t', min_size=1, max_size=10)
    )
    def test_username_with_surrounding_whitespace(self, valid_text, whitespace_prefix, whitespace_suffix):
        """
        Property: Usernames with surrounding whitespace are handled correctly.
        Validates: Requirements 3.1, 3.6
        """
        username_with_whitespace = whitespace_prefix + valid_text + whitespace_suffix
        
        # Skip if too long
        if len(username_with_whitespace) > 200:
            return
        
        # Validation should handle this (strip is done in blueprint)
        # The validator itself checks if stripped version is empty
        valid, error = InputValidator.validate_username(username_with_whitespace)
        
        # Should pass if the text itself is not empty after stripping
        assert valid is True or (not valid and len(username_with_whitespace.strip()) == 0)
