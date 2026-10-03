"""
Authentication blueprint for user login, registration, and logout.
Implements secure authentication with input validation and session management.
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.auth_service import AuthService
from app.validators.input_validator import InputValidator


# Create authentication blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login route with input validation.
    
    GET: Display login form
    POST: Process login credentials
    
    Security Features:
        - Input validation for username and password
        - Generic error messages prevent username enumeration
        - Secure session management
        - Flash messages for user feedback
    
    Returns:
        GET: Rendered login template
        POST: Redirect to users list on success, login form with errors on failure
    """
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Validate username
        valid_username, username_error = InputValidator.validate_username(username)
        if not valid_username:
            flash(username_error, 'error')
            return render_template('auth/login.html')
        
        # Validate password
        valid_password, password_error = InputValidator.validate_password(password)
        if not valid_password:
            flash(password_error, 'error')
            return render_template('auth/login.html')
        
        # Authenticate user
        success, user, error = AuthService.authenticate_user(username, password)
        
        if success:
            # Store user information in session
            session['user_id'] = user.id
            session['username'] = user.username
            # Mark session as permanent to enforce timeout
            session.permanent = True
            
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(url_for('users.list_users'))
        else:
            # Display generic error message
            flash(error, 'error')
            return render_template('auth/login.html')
    
    # GET request - display login form
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration route with comprehensive input validation.
    
    GET: Display registration form
    POST: Process registration data
    
    Security Features:
        - Comprehensive input validation for all fields
        - Password hashing with bcrypt (cost factor 12)
        - SQLAlchemy ORM prevents SQL injection
        - Flash messages for user feedback
        - Validation errors displayed to user
    
    Returns:
        GET: Rendered registration template
        POST: Redirect to login on success, registration form with errors on failure
    """
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        gender = request.form.get('gender', '')
        
        # Validate all inputs
        errors = []
        
        # Validate username
        valid_username, username_error = InputValidator.validate_username(username)
        if not valid_username:
            errors.append(username_error)
        
        # Validate email
        valid_email, email_error = InputValidator.validate_email(email)
        if not valid_email:
            errors.append(email_error)
        
        # Validate password
        valid_password, password_error = InputValidator.validate_password(password)
        if not valid_password:
            errors.append(password_error)
        
        # Validate gender
        valid_gender, gender_error = InputValidator.validate_gender(gender)
        if not valid_gender:
            errors.append(gender_error)
        
        # If there are validation errors, display them and return to form
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/register.html')
        
        # Register user
        success, error = AuthService.register_user(username, email, password, gender)
        
        if success:
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('auth.login'))
        else:
            # Display registration error
            flash(error, 'error')
            return render_template('auth/register.html')
    
    # GET request - display registration form
    return render_template('auth/register.html')


@auth_bp.route('/logout')
def logout():
    """
    Logout route to clear session.
    
    Security Features:
        - Clears all session data
        - Flash message for user feedback
        - Redirects to login page
    
    Returns:
        Redirect to login page
    """
    # Clear all session data
    session.clear()
    
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))
