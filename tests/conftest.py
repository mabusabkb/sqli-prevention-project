"""
Pytest configuration and fixtures.
Provides common test fixtures for all test modules.
"""
import pytest
from app import create_app, db as _db
from app.models import User  # Import models to register them with SQLAlchemy


@pytest.fixture(scope='session')
def app():
    """
    Create Flask application for testing.
    Session-scoped fixture - created once per test session.
    """
    app = create_app('testing')
    
    # Establish application context
    ctx = app.app_context()
    ctx.push()
    
    yield app
    
    # Teardown
    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """
    Create database for testing.
    Session-scoped fixture - created once per test session.
    """
    # Import models to ensure they're registered
    from app.models import User
    
    # Create all tables
    _db.create_all()
    
    yield _db
    
    # Teardown - drop all tables
    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def clean_db(db):
    """
    Clean database before each test.
    Function-scoped fixture - runs before each test function.
    """
    yield
    
    # Clean up after test
    db.session.remove()
    # Delete all data from tables
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


@pytest.fixture(scope='function')
def client(app):
    """
    Create Flask test client.
    Function-scoped fixture - created for each test function.
    """
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """
    Create Flask CLI test runner.
    Function-scoped fixture - created for each test function.
    """
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def app_context(app):
    """
    Provide application context for tests.
    Function-scoped fixture - created for each test function.
    This is used by property tests that need database access.
    """
    # Context is already pushed in the app fixture
    # This fixture just provides a convenient way to access it
    return app
