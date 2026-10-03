"""
Test script for MySQL migration.
This script demonstrates how to test the migration on MySQL.

Prerequisites:
1. MySQL server running (locally or via Docker)
2. PyMySQL installed: pip install PyMySQL cryptography

Usage:
    python test_mysql_migration.py
"""
import os
import sys
import pymysql
from app import create_app, db
from sqlalchemy import inspect


def test_mysql_migration():
    """Test the migration on MySQL database"""
    
    # MySQL connection parameters
    mysql_host = os.environ.get('MYSQL_HOST', 'localhost')
    mysql_port = int(os.environ.get('MYSQL_PORT', 3306))
    mysql_user = os.environ.get('MYSQL_USER', 'root')
    mysql_password = os.environ.get('MYSQL_PASSWORD', '')
    mysql_database = 'flask_test_db'
    
    print("=" * 60)
    print("MySQL Migration Test")
    print("=" * 60)
    
    # Step 1: Install PyMySQL as MySQLdb
    pymysql.install_as_MySQLdb()
    print("\n✓ PyMySQL installed as MySQLdb")
    
    # Step 2: Connect to MySQL and create test database
    try:
        print(f"\n→ Connecting to MySQL at {mysql_host}:{mysql_port}...")
        conn = pymysql.connect(
            host=mysql_host,
            port=mysql_port,
            user=mysql_user,
            password=mysql_password
        )
        cursor = conn.cursor()
        
        # Drop database if exists
        cursor.execute(f"DROP DATABASE IF EXISTS {mysql_database}")
        print(f"✓ Dropped existing database '{mysql_database}' (if any)")
        
        # Create database
        cursor.execute(f"CREATE DATABASE {mysql_database} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        print(f"✓ Created database '{mysql_database}'")
        
        cursor.close()
        conn.close()
        
    except pymysql.Error as e:
        print(f"\n✗ MySQL connection error: {e}")
        print("\nPlease ensure:")
        print("  1. MySQL server is running")
        print("  2. Connection parameters are correct")
        print("  3. User has CREATE DATABASE privileges")
        sys.exit(1)
    
    # Step 3: Set up Flask app with MySQL
    mysql_url = f"mysql://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_database}"
    os.environ['DATABASE_URL'] = mysql_url
    
    print(f"\n→ Creating Flask app with MySQL database...")
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = mysql_url
    
    with app.app_context():
        # Step 4: Run migration
        print("\n→ Running migration...")
        db.create_all()
        print("✓ Migration completed successfully")
        
        # Step 5: Verify schema
        print("\n→ Verifying database schema...")
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'users' not in tables:
            print("✗ Users table not found!")
            sys.exit(1)
        
        print(f"✓ Found tables: {tables}")
        
        # Verify columns
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        expected_columns = ['id', 'username', 'email', 'password', 'gender', 'created_at']
        
        print(f"✓ Users table columns: {column_names}")
        
        for col in expected_columns:
            if col not in column_names:
                print(f"✗ Missing column: {col}")
                sys.exit(1)
        
        print("✓ All expected columns present")
        
        # Verify indexes
        indexes = inspector.get_indexes('users')
        print(f"✓ Indexes: {[idx['name'] for idx in indexes]}")
        
        # Verify unique constraints
        unique_constraints = inspector.get_unique_constraints('users')
        print(f"✓ Unique constraints: {[uc['name'] for uc in unique_constraints]}")
        
        # Step 6: Test CRUD operations
        print("\n→ Testing CRUD operations...")
        from app.models.user import User
        from flask_bcrypt import Bcrypt
        
        bcrypt = Bcrypt(app)
        
        # Create test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password=bcrypt.generate_password_hash('password123').decode('utf-8'),
            gender='Male'
        )
        db.session.add(test_user)
        db.session.commit()
        print("✓ Created test user")
        
        # Read user
        user = User.query.filter_by(username='testuser').first()
        if not user:
            print("✗ Failed to read user")
            sys.exit(1)
        print(f"✓ Read user: {user.username} ({user.email})")
        
        # Update user
        user.email = 'updated@example.com'
        db.session.commit()
        print("✓ Updated user email")
        
        # Verify update
        user = User.query.filter_by(username='testuser').first()
        if user.email != 'updated@example.com':
            print("✗ Update verification failed")
            sys.exit(1)
        print("✓ Verified update")
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        print("✓ Deleted user")
        
        # Verify deletion
        user = User.query.filter_by(username='testuser').first()
        if user:
            print("✗ Deletion verification failed")
            sys.exit(1)
        print("✓ Verified deletion")
    
    # Step 7: Cleanup
    print("\n→ Cleaning up...")
    conn = pymysql.connect(
        host=mysql_host,
        port=mysql_port,
        user=mysql_user,
        password=mysql_password
    )
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE {mysql_database}")
    cursor.close()
    conn.close()
    print(f"✓ Dropped test database '{mysql_database}'")
    
    print("\n" + "=" * 60)
    print("✓ All MySQL migration tests passed!")
    print("=" * 60)


if __name__ == '__main__':
    test_mysql_migration()
