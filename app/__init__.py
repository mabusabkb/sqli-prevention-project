"""
Flask application factory.
Creates and configures the Flask application with all extensions and blueprints.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from config import config


# Initialize extensions (without app instance)
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


def create_app(config_name=None):
    """
    Application factory function.
    
    Args:
        config_name: Configuration name ('development', 'testing', 'production')
                    If None, uses FLASK_ENV environment variable or 'default'
    
    Returns:
        Configured Flask application instance
    """
    # Create Flask app
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    app.config.from_object(config[config_name])
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    
    # Test database connection
    with app.app_context():
        try:
            # Verify database connection
            db.engine.connect()
            app.logger.info(f'Database connection successful: {app.config["SQLALCHEMY_DATABASE_URI"]}')
        except Exception as e:
            app.logger.error(f'Database connection failed: {str(e)}')
            if config_name == 'production':
                raise RuntimeError(f'Failed to connect to database in production: {str(e)}')
            else:
                app.logger.warning('Continuing without database connection in non-production environment')
    
    # Register blueprints
    from app.blueprints.auth import auth_bp
    from app.blueprints.users import users_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    
    # Register health check route
    @app.route('/health')
    def health_check():
        """Health check endpoint for monitoring"""
        try:
            # Test database connection using text() for SQLAlchemy 2.0 compatibility
            from sqlalchemy import text
            db.session.execute(text('SELECT 1'))
            db_status = 'connected'
        except Exception as e:
            app.logger.error(f'Database health check failed: {str(e)}')
            db_status = 'disconnected'
        
        return {
            'status': 'healthy' if db_status == 'connected' else 'unhealthy',
            'environment': config_name,
            'database': db_status
        }, 200 if db_status == 'connected' else 503
    
    @app.route('/')
    def index():
        """Root endpoint"""
        return {
            'message': 'Secure Flask SQL Injection Prevention Application',
            'version': '1.0.0',
            'status': 'running'
        }, 200
    
    # Configure logging
    configure_logging(app)
    
    # Register error handlers
    register_error_handlers(app)
    
    # Create database tables (in development)
    with app.app_context():
        if config_name == 'development':
            db.create_all()
    
    return app


def configure_logging(app):
    """
    Configure secure logging for the application.
    
    Args:
        app: Flask application instance
    """
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # Configure rotating file handler
        file_handler = RotatingFileHandler(
            'logs/flask_app.log',
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        
        # Set log format
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        # Set log level
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        app.logger.setLevel(logging.INFO)
        app.logger.info('Flask application startup')


def register_error_handlers(app):
    """
    Register error handlers for common HTTP errors.
    
    Args:
        app: Flask application instance
    """
    from sqlalchemy.exc import SQLAlchemyError, OperationalError, DatabaseError
    
    @app.errorhandler(SQLAlchemyError)
    def handle_database_error(error):
        """Handle SQLAlchemy database errors"""
        db.session.rollback()
        app.logger.error(f'Database error: {str(error)}')
        return {'error': 'A database error occurred. Please try again later.'}, 500
    
    @app.errorhandler(OperationalError)
    def handle_operational_error(error):
        """Handle database operational errors (connection issues)"""
        db.session.rollback()
        app.logger.error(f'Database operational error: {str(error)}')
        return {'error': 'Database connection error. Please try again later.'}, 503
    
    @app.errorhandler(400)
    def bad_request_error(error):
        """Handle 400 Bad Request errors"""
        app.logger.warning(f'Bad request: {error}')
        return {'error': 'Bad request'}, 400
    
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 Not Found errors"""
        app.logger.warning(f'Page not found: {error}')
        return {'error': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 Internal Server errors"""
        db.session.rollback()
        app.logger.error(f'Internal server error: {error}')
        return {'error': 'An internal error occurred. Please try again later.'}, 500
