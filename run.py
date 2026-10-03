"""
Application entry point.
Run this file to start the Flask development server.
"""
import os
from app import create_app
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = create_app(os.environ.get('FLASK_ENV', 'development'))


if __name__ == '__main__':
    # Run development server
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        debug=app.config['DEBUG']
    )
