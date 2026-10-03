# Database Migration Testing Guide

This guide explains how to test Alembic migrations on both SQLite (development) and MySQL (production simulation).

## Table of Contents

1. [SQLite Testing (Development)](#sqlite-testing-development)
2. [MySQL Testing (Production Simulation)](#mysql-testing-production-simulation)
3. [Migration Commands Reference](#migration-commands-reference)
4. [Troubleshooting](#troubleshooting)

---

## SQLite Testing (Development)

SQLite is the default database for development and requires no additional setup.

### Prerequisites

- Python virtual environment activated
- Flask-Migrate installed (included in requirements.txt)

### Testing Steps

#### 1. Create a Migration

```bash
# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Generate migration from model changes
flask db migrate -m "Description of changes"
```

#### 2. Review the Migration

Check the generated migration file in `migrations/versions/`:

```bash
ls -la migrations/versions/
```

Review the `upgrade()` and `downgrade()` functions to ensure they're correct.

#### 3. Apply the Migration

```bash
flask db upgrade
```

#### 4. Verify the Schema

```bash
python -c "
from app import create_app, db
from sqlalchemy import inspect

app = create_app('development')
with app.app_context():
    inspector = inspect(db.engine)
    print('Tables:', inspector.get_table_names())
    print('Users columns:', [c['name'] for c in inspector.get_columns('users')])
"
```

#### 5. Test Rollback

```bash
# Downgrade to previous version
flask db downgrade

# Verify table was removed
python -c "
from app import create_app, db
from sqlalchemy import inspect

app = create_app('development')
with app.app_context():
    inspector = inspect(db.engine)
    print('Tables:', inspector.get_table_names())
"

# Re-apply migration
flask db upgrade
```

#### 6. Test CRUD Operations

```bash
python -c "
from app import create_app, db
from app.models.user import User
from flask_bcrypt import Bcrypt

app = create_app('development')
bcrypt = Bcrypt(app)

with app.app_context():
    # Create
    user = User(
        username='testuser',
        email='test@example.com',
        password=bcrypt.generate_password_hash('password123').decode('utf-8'),
        gender='Male'
    )
    db.session.add(user)
    db.session.commit()
    print('✓ Created user:', user.id)
    
    # Read
    user = User.query.filter_by(username='testuser').first()
    print('✓ Read user:', user.username, user.email)
    
    # Update
    user.email = 'updated@example.com'
    db.session.commit()
    print('✓ Updated user email')
    
    # Delete
    db.session.delete(user)
    db.session.commit()
    print('✓ Deleted user')
"
```

---

## MySQL Testing (Production Simulation)

MySQL testing simulates a production environment to ensure migrations work correctly with MySQL-specific features.

### Prerequisites

1. **MySQL Server** (choose one option):
   - Docker (recommended)
   - Local MySQL installation
   - Remote MySQL server

2. **Python MySQL Driver**:
   ```bash
   pip install PyMySQL cryptography
   ```

### Option 1: Using Docker (Recommended)

#### 1. Start MySQL Container

```bash
# Start MySQL using Docker Compose
docker-compose -f docker-compose.mysql-test.yml up -d

# Wait for MySQL to be ready (about 30 seconds)
docker-compose -f docker-compose.mysql-test.yml ps

# Check logs
docker-compose -f docker-compose.mysql-test.yml logs mysql
```

#### 2. Run Migration Test Script

```bash
# Set environment variables
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=testpassword

# Run test script
python test_mysql_migration.py
```

#### 3. Manual Testing (Alternative)

```bash
# Set database URL
export DATABASE_URL="mysql://root:testpassword@localhost:3306/flask_test_db"

# Create database
docker exec flask_mysql_test mysql -uroot -ptestpassword -e "CREATE DATABASE IF NOT EXISTS flask_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"

# Run migrations
flask db upgrade

# Verify schema
python -c "
import pymysql
pymysql.install_as_MySQLdb()

from app import create_app, db
from sqlalchemy import inspect

app = create_app('production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:testpassword@localhost:3306/flask_test_db'

with app.app_context():
    inspector = inspect(db.engine)
    print('Tables:', inspector.get_table_names())
    print('Users columns:', [c['name'] for c in inspector.get_columns('users')])
"
```

#### 4. Stop MySQL Container

```bash
# Stop and remove container
docker-compose -f docker-compose.mysql-test.yml down

# Remove volumes (optional - cleans up all data)
docker-compose -f docker-compose.mysql-test.yml down -v
```

### Option 2: Using Local MySQL

#### 1. Install MySQL

**macOS:**
```bash
brew install mysql
brew services start mysql
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install mysql-server
sudo systemctl start mysql
```

**Windows:**
Download and install from [MySQL Downloads](https://dev.mysql.com/downloads/installer/)

#### 2. Create Test Database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE flask_test_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'flask_user'@'localhost' IDENTIFIED BY 'flask_password';
GRANT ALL PRIVILEGES ON flask_test_db.* TO 'flask_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

#### 3. Run Migration Test

```bash
# Set environment variables
export MYSQL_HOST=localhost
export MYSQL_PORT=3306
export MYSQL_USER=flask_user
export MYSQL_PASSWORD=flask_password

# Run test script
python test_mysql_migration.py
```

---

## Migration Commands Reference

### Common Commands

```bash
# Initialize migrations (already done)
flask db init

# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback one migration
flask db downgrade

# Show current migration version
flask db current

# Show migration history
flask db history

# Rollback to specific version
flask db downgrade <revision_id>

# Upgrade to specific version
flask db upgrade <revision_id>
```

### Migration File Structure

```python
"""Description of migration

Revision ID: abc123
Revises: xyz789
Create Date: 2024-01-01 12:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'xyz789'
branch_labels = None
depends_on = None

def upgrade():
    # Commands to apply the migration
    pass

def downgrade():
    # Commands to rollback the migration
    pass
```

### Best Practices

1. **Always review generated migrations** before applying them
2. **Test migrations on a copy of production data** before deploying
3. **Keep migrations small and focused** on a single change
4. **Write descriptive migration messages** that explain what changed
5. **Test both upgrade and downgrade** paths
6. **Never edit applied migrations** - create a new migration instead
7. **Backup database** before running migrations in production

---

## Troubleshooting

### Issue: "No changes in schema detected"

**Cause:** Models not imported in `migrations/env.py`

**Solution:** Ensure models are imported:
```python
# migrations/env.py
from app.models import user  # Import all model modules
```

### Issue: "Can't connect to MySQL server"

**Cause:** MySQL server not running or wrong connection parameters

**Solution:**
1. Check if MySQL is running: `docker ps` or `systemctl status mysql`
2. Verify connection parameters (host, port, user, password)
3. Check firewall settings

### Issue: "Access denied for user"

**Cause:** Incorrect credentials or insufficient privileges

**Solution:**
1. Verify username and password
2. Grant necessary privileges:
   ```sql
   GRANT ALL PRIVILEGES ON database_name.* TO 'user'@'host';
   FLUSH PRIVILEGES;
   ```

### Issue: "Table already exists"

**Cause:** Database not in sync with migrations

**Solution:**
1. Drop the database and recreate it
2. Or stamp the current version:
   ```bash
   flask db stamp head
   ```

### Issue: Migration generates wrong SQL

**Cause:** Alembic auto-detection limitations

**Solution:**
1. Manually edit the migration file
2. Review the `upgrade()` and `downgrade()` functions
3. Test thoroughly before applying

### Issue: "ModuleNotFoundError: No module named 'MySQLdb'"

**Cause:** MySQL driver not installed

**Solution:**
```bash
# Install PyMySQL (pure Python, no C dependencies)
pip install PyMySQL cryptography

# Add to your app initialization
import pymysql
pymysql.install_as_MySQLdb()
```

---

## Testing Checklist

### SQLite Testing
- [ ] Migration file generated successfully
- [ ] Migration applies without errors (`flask db upgrade`)
- [ ] Schema matches model definition
- [ ] Rollback works correctly (`flask db downgrade`)
- [ ] CRUD operations work
- [ ] Unique constraints enforced
- [ ] Check constraints enforced

### MySQL Testing
- [ ] MySQL server accessible
- [ ] Database created successfully
- [ ] Migration applies without errors
- [ ] Schema matches model definition
- [ ] Character set is utf8mb4
- [ ] Collation is utf8mb4_unicode_ci
- [ ] Indexes created correctly
- [ ] Foreign keys work (if applicable)
- [ ] CRUD operations work
- [ ] Unique constraints enforced
- [ ] Check constraints enforced

---

## Additional Resources

- [Flask-Migrate Documentation](https://flask-migrate.readthedocs.io/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [MySQL Documentation](https://dev.mysql.com/doc/)

````