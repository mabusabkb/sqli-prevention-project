"""
User model for the Flask application.
Uses SQLAlchemy ORM to prevent SQL injection vulnerabilities.
"""
from datetime import datetime
from app import db


class User(db.Model):
    """
    User model representing the users table.
    
    This model uses SQLAlchemy's declarative base, which automatically
    generates parameterized queries to prevent SQL injection attacks.
    
    Attributes:
        id: Primary key with auto-increment
        username: Unique username (max 200 characters)
        email: Unique email address (max 200 characters)
        password: Bcrypt hashed password (max 200 characters)
        gender: User gender (Male or Female)
        created_at: Timestamp of user creation
    """
    __tablename__ = 'users'
    
    # Primary key with auto-increment
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # User credentials and information
    username = db.Column(db.String(200), nullable=False, unique=True)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)  # Stores bcrypt hash
    gender = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        db.CheckConstraint("gender IN ('Male', 'Female')", name='check_gender'),
    )
    
    def __repr__(self):
        """
        String representation for debugging.
        
        Returns:
            String representation of the User object
        """
        return f'<User {self.username}>'
    
    def to_dict(self):
        """
        Convert user to dictionary representation.
        Excludes password field for security.
        
        Returns:
            Dictionary containing user data (without password)
        """
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'gender': self.gender,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
