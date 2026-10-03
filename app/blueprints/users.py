"""
User management blueprint for CRUD operations.
Implements secure user management with input validation and SQLAlchemy ORM.
"""
from flask import Blueprint, render_template, request, session, redirect, url_for, flash
from functools import wraps
from app.services.user_service import UserService
from app.validators.input_validator import InputValidator


# Create users blueprint
users_bp = Blueprint('users', __name__, url_prefix='/users')


def login_required(f):
    """
    Decorator to require login for routes.
    
    Args:
        f: Function to wrap
    
    Returns:
        Wrapped function that checks for user_id in session
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@users_bp.route('/')
@login_required
def list_users():
    """
    Display all users.
    
    Retrieves all users from the database using UserService and displays them
    in a table format. Uses SQLAlchemy ORM to prevent SQL injection.
    
    Returns:
        Rendered users list template with all users
        
    Security Features:
        - Login required decorator ensures authentication
        - SQLAlchemy ORM prevents SQL injection
        - Password field excluded from display via to_dict()
    """
    success, users, error = UserService.get_all_users()
    
    if not success:
        flash(error, 'error')
        users = []
    
    return render_template('users/list.html', users=users)


@users_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_user():
    """
    Create a new user.
    
    GET: Display user creation form
    POST: Validate inputs and create user in database
    
    Returns:
        GET: Rendered create user form
        POST: Redirect to users list on success, or form with errors on failure
        
    Security Features:
        - Login required decorator ensures authentication
        - InputValidator validates all form inputs
        - UserService uses SQLAlchemy ORM to prevent SQL injection
        - Password hashed with bcrypt before storage
    """
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        gender = request.form.get('gender', '')
        
        # Validate all inputs
        errors = []
        
        valid_username, username_error = InputValidator.validate_username(username)
        if not valid_username:
            errors.append(username_error)
        
        valid_email, email_error = InputValidator.validate_email(email)
        if not valid_email:
            errors.append(email_error)
        
        valid_password, password_error = InputValidator.validate_password(password)
        if not valid_password:
            errors.append(password_error)
        
        valid_gender, gender_error = InputValidator.validate_gender(gender)
        if not valid_gender:
            errors.append(gender_error)
        
        # If validation errors, display them and return to form
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('users/create.html', 
                                   username=username, 
                                   email=email, 
                                   gender=gender)
        
        # Create user using UserService
        success, error = UserService.create_user(username, email, password, gender)
        
        if success:
            flash('User created successfully!', 'success')
            return redirect(url_for('users.list_users'))
        else:
            flash(error, 'error')
            return render_template('users/create.html', 
                                   username=username, 
                                   email=email, 
                                   gender=gender)
    
    # GET request - display empty form
    return render_template('users/create.html')


@users_bp.route('/update/<user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    """
    Update an existing user.
    
    GET: Display user update form with current user data
    POST: Validate inputs and update user in database
    
    Args:
        user_id: The ID of the user to update (from URL parameter)
    
    Returns:
        GET: Rendered update user form with current user data
        POST: Redirect to users list on success, or form with errors on failure
        
    Security Features:
        - Login required decorator ensures authentication
        - InputValidator validates user_id and all form inputs
        - UserService uses SQLAlchemy ORM to prevent SQL injection
        - Password hashed with bcrypt before storage
    """
    # Validate user_id parameter
    valid_id, id_int, id_error = InputValidator.validate_id(user_id)
    if not valid_id:
        flash(id_error, 'error')
        return redirect(url_for('users.list_users'))
    
    if request.method == 'POST':
        # Get form data
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        gender = request.form.get('gender', '')
        
        # Validate all inputs
        errors = []
        
        valid_username, username_error = InputValidator.validate_username(username)
        if not valid_username:
            errors.append(username_error)
        
        valid_email, email_error = InputValidator.validate_email(email)
        if not valid_email:
            errors.append(email_error)
        
        valid_password, password_error = InputValidator.validate_password(password)
        if not valid_password:
            errors.append(password_error)
        
        valid_gender, gender_error = InputValidator.validate_gender(gender)
        if not valid_gender:
            errors.append(gender_error)
        
        # If validation errors, display them and return to form
        if errors:
            for error in errors:
                flash(error, 'error')
            # Fetch user data to repopulate form
            success, user, fetch_error = UserService.get_user_by_id(id_int)
            if not success:
                flash(fetch_error, 'error')
                return redirect(url_for('users.list_users'))
            return render_template('users/update.html', user=user)
        
        # Update user using UserService
        success, error = UserService.update_user(id_int, username, email, password, gender)
        
        if success:
            flash('User updated successfully!', 'success')
            return redirect(url_for('users.list_users'))
        else:
            flash(error, 'error')
            # Fetch user data to repopulate form
            success, user, fetch_error = UserService.get_user_by_id(id_int)
            if not success:
                flash(fetch_error, 'error')
                return redirect(url_for('users.list_users'))
            return render_template('users/update.html', user=user)
    
    # GET request - fetch user data and display form
    success, user, error = UserService.get_user_by_id(id_int)
    
    if not success:
        flash(error, 'error')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/update.html', user=user)


@users_bp.route('/delete/<user_id>')
@login_required
def delete_user(user_id):
    """
    Delete a user.
    
    Validates the user_id and deletes the user from the database.
    This is a GET route for simplicity, but in production should use POST/DELETE
    with CSRF protection.
    
    Args:
        user_id: The ID of the user to delete (from URL parameter)
    
    Returns:
        Redirect to users list with success or error message
        
    Security Features:
        - Login required decorator ensures authentication
        - InputValidator validates user_id
        - UserService uses SQLAlchemy ORM to prevent SQL injection
        
    Note:
        In production, this should be a POST/DELETE request with CSRF protection.
        Using GET for simplicity in this demonstration.
    """
    # Validate user_id parameter
    valid_id, id_int, id_error = InputValidator.validate_id(user_id)
    if not valid_id:
        flash(id_error, 'error')
        return redirect(url_for('users.list_users'))
    
    # Delete user using UserService
    success, error = UserService.delete_user(id_int)
    
    if success:
        flash('User deleted successfully!', 'success')
    else:
        flash(error, 'error')
    
    return redirect(url_for('users.list_users'))
