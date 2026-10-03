"""
Test to verify project setup is correct.
"""
import pytest
from app import create_app, db


def test_app_creation():
    """Test that Flask app can be created"""
    app = create_app('testing')
    assert app is not None
    assert app.config['TESTING'] is True


def test_app_context():
    """Test that app context works"""
    app = create_app('testing')
    with app.app_context():
        assert db is not None


def test_development_config():
    """Test development configuration"""
    app = create_app('development')
    assert app.config['DEBUG'] is True
    assert 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']


def test_testing_config():
    """Test testing configuration"""
    app = create_app('testing')
    assert app.config['TESTING'] is True
    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'


def test_extensions_initialized():
    """Test that extensions are initialized"""
    app = create_app('testing')
    with app.app_context():
        # Test database extension
        assert db.engine is not None
