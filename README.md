# Secure Flask SQL Injection Prevention Application

A production-ready Flask application demonstrating comprehensive SQL injection prevention using SQLAlchemy ORM, secure authentication with bcrypt, and property-based testing.

## Project Overview

This application transforms an existing PHP-based web application into a secure Python Flask application with:

- **SQL Injection Prevention**: All database operations use SQLAlchemy ORM with parameterized queries
- **Secure Authentication**: Bcrypt password hashing with cost factor 12
- **Input Validation**: Comprehensive validation and sanitization of all user inputs
- **Error Handling**: Secure error handling without information disclosure
- **Property-Based Testing**: Hypothesis-based tests to verify security properties
- **Production Ready**: Docker support and deployment configurations

## Project Structure

```
flask_app/
├── app/                        # Application package
│   ├── __init__.py            # Application factory
│   ├── models/                # Database models
│   ├── blueprints/            # Route blueprints
│   ├── services/              # Business logic
│   ├── validators/            # Input validation
│   ├── templates/             # HTML templates
│   └── static/                # CSS, JavaScript, images
├── tests/                      # Test suite
│   ├── unit/                  # Unit tests
│   ├── integration/           # Integration tests
│   └── property/              # Property-based tests
├── migrations/                 # Database migrations
├── config.py                   # Configuration classes
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
└── run.py                     # Application entry point
```

## Requirements

- Python 3.9 or higher
- pip (Python package manager)
- Virtual environment (recommended)

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd flask_app
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
FLASK_APP=run.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///dev.db
```

**Generate a secure secret key:**

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 5. Initialize Database

The database migrations are managed using Flask-Migrate (Alembic). The initial migration for the users table is already created.

```bash
# Apply migrations to create the database schema
flask db upgrade

# Verify the database was created
python -c "from app import create_app, db; from sqlalchemy import inspect; app = create_app('development'); app.app_context().push(); inspector = inspect(db.engine); print('Tables:', inspector.get_table_names())"
```

**Migration Commands:**

```bash
# Create a new migration after model changes
flask db migrate -m "Description of changes"

# Apply pending migrations
flask db upgrade

# Rollback the last migration
flask db downgrade

# Show current migration version
flask db current

# Show migration history
flask db history
```

For detailed migration testing instructions (including MySQL testing), see [MIGRATION_TESTING.md](MIGRATION_TESTING.md).

### 6. Run the Application

```bash
# Development server
python run.py

# Or using Flask CLI
flask run
```

The application will be available at `http://localhost:5000`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest tests/property/       # Property-based tests only

# Run specific test file
pytest tests/unit/test_validators.py
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `FLASK_APP` | Application entry point | `run.py` | Yes |
| `FLASK_ENV` | Environment (development/testing/production) | `development` | No |
| `SECRET_KEY` | Secret key for session management | Auto-generated in dev | Yes (production) |
| `DATABASE_URL` | Database connection string | `sqlite:///dev.db` | Yes (production) |
| `DEBUG` | Enable debug mode | `True` (dev) | No |

## Database Configuration

### SQLite (Development)

```env
DATABASE_URL=sqlite:///dev.db
```

SQLite is the default database for development. It requires no additional setup and stores data in the `instance/dev.db` file.

### MySQL (Production)

```env
DATABASE_URL=mysql://username:password@localhost:3306/database_name
```

**Note**: MySQL requires a MySQL driver. We recommend PyMySQL (pure Python, no C dependencies):

```bash
pip install PyMySQL cryptography
```

Add to your application initialization (already configured in `app/__init__.py`):
```python
import pymysql
pymysql.install_as_MySQLdb()
```

**Alternative**: For better performance, use `mysqlclient` (requires MySQL development libraries):

```bash
# Install MySQL development libraries first
# macOS: brew install mysql
# Ubuntu: apt-get install default-libmysqlclient-dev

pip install mysqlclient
```

### PostgreSQL (Production)

```env
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

**Note**: PostgreSQL requires `psycopg2`:
```bash
pip install psycopg2-binary
```

### Database Migrations

The project uses Flask-Migrate (Alembic) for database schema management. The initial migration for the users table is already created in `migrations/versions/`.

**Common Migration Workflows:**

1. **Apply migrations** (create/update database schema):
   ```bash
   flask db upgrade
   ```

2. **Create a new migration** after modifying models:
   ```bash
   flask db migrate -m "Add new field to User model"
   ```

3. **Rollback a migration**:
   ```bash
   flask db downgrade
   ```

4. **View migration history**:
   ```bash
   flask db history
   ```

For comprehensive migration testing instructions (including MySQL testing with Docker), see [MIGRATION_TESTING.md](MIGRATION_TESTING.md).

## Security Features

### 1. SQL Injection Prevention

All database operations use SQLAlchemy ORM, which automatically generates parameterized queries:

```python
# SECURE: SQLAlchemy ORM
user = User.query.filter_by(username=username).first()

# Generated SQL: SELECT * FROM users WHERE username = ?
# Parameters: [username]
```

### 2. Password Security

- Bcrypt hashing with cost factor 12
- Automatic salt generation
- Constant-time password verification

### 3. Input Validation

- Length constraints (max 200 characters)
- Email format validation
- Whitespace rejection
- Gender whitelist validation

### 4. Error Handling

- Generic error messages to users
- Detailed logging for debugging
- No information disclosure

### 5. Session Security

- Signed cookies
- HttpOnly flag
- SameSite protection
- Session expiration

## Development Workflow

### Adding a New Feature

1. Create database model in `app/models/`
2. Create service layer in `app/services/`
3. Create validators in `app/validators/`
4. Create blueprint in `app/blueprints/`
5. Register blueprint in `app/__init__.py`
6. Create templates in `app/templates/`
7. Write tests in `tests/`

### Creating a Database Migration

```bash
# After modifying models
flask db migrate -m "Description of changes"

# Review the generated migration in migrations/versions/

# Apply the migration
flask db upgrade
```

### Rolling Back a Migration

```bash
flask db downgrade
```

## Production Deployment

### Using Docker

```bash
# Build image
docker build -t flask-app .

# Run container
docker run -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=your-database-url \
  flask-app
```

### Using Gunicorn

```bash
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

### Environment Setup

1. Set all required environment variables
2. Use a production database (MySQL/PostgreSQL)
3. Enable HTTPS
4. Set `FLASK_ENV=production`
5. Configure security headers
6. Set up logging and monitoring

## Project Status

**Current Phase**: Task 1 - Project Setup and Infrastructure ✅

- [x] Initialize Flask project structure with application factory pattern
- [x] Create directory structure (app/, tests/, migrations/, config.py)
- [x] Set up virtual environment
- [x] Install core dependencies (Flask, SQLAlchemy, Flask-Bcrypt, Flask-Migrate)
- [x] Create requirements.txt
- [x] Initialize Git repository with .gitignore
- [x] Create .env.example with placeholder configuration values

**Next Steps**:
- Task 2: Database models and schema
- Task 3: Input validation layer
- Task 4: Authentication system
- Task 5: User management CRUD operations
- Task 6: Property-based testing
- Task 7: Frontend templates
- Task 8: Deployment configuration

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Ensure all tests pass
5. Submit a pull request

## License

[Your License Here]

## Contact

[Your Contact Information]

````