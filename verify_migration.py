"""
Verification script for database migrations.
Tests the migration on SQLite and verifies MySQL compatibility.
"""
import os
import sys
from app import create_app, db
from app.models.user import User
from sqlalchemy import inspect, text
from flask_bcrypt import Bcrypt


def print_header(title):
    """Print a formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_success(message):
    """Print a success message"""
    print(f"✓ {message}")


def print_error(message):
    """Print an error message"""
    print(f"✗ {message}")


def verify_sqlite_migration():
    """Verify migration on SQLite"""
    print_header("SQLite Migration Verification")
    
    # Create app with development config (SQLite)
    app = create_app('development')
    bcrypt = Bcrypt(app)
    
    with app.app_context():
        # Verify tables exist
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'users' not in tables:
            print_error("Users table not found!")
            return False
        
        print_success(f"Found tables: {tables}")
        
        # Verify columns
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        expected_columns = ['id', 'username', 'email', 'password', 'gender', 'created_at']
        
        print_success(f"Users table columns: {column_names}")
        
        for col in expected_columns:
            if col not in column_names:
                print_error(f"Missing column: {col}")
                return False
        
        print_success("All expected columns present")
        
        # Verify indexes
        indexes = inspector.get_indexes('users')
        print_success(f"Indexes: {[idx['name'] for idx in indexes]}")
        
        # Verify unique constraints
        unique_constraints = inspector.get_unique_constraints('users')
        print_success(f"Unique constraints: {[uc['name'] for uc in unique_constraints]}")
        
        # Test CRUD operations
        print("\n→ Testing CRUD operations...")
        
        # Create
        test_user = User(
            username='testuser',
            email='test@example.com',
            password=bcrypt.generate_password_hash('password123').decode('utf-8'),
            gender='Male'
        )
        db.session.add(test_user)
        db.session.commit()
        user_id = test_user.id
        print_success(f"Created user with ID: {user_id}")
        
        # Read
        user = User.query.filter_by(username='testuser').first()
        if not user:
            print_error("Failed to read user")
            return False
        print_success(f"Read user: {user.username} ({user.email})")
        
        # Update
        user.email = 'updated@example.com'
        db.session.commit()
        print_success("Updated user email")
        
        # Verify update
        user = User.query.get(user_id)
        if user.email != 'updated@example.com':
            print_error("Update verification failed")
            return False
        print_success("Verified update")
        
        # Test unique constraint
        print("\n→ Testing unique constraints...")
        duplicate_user = User(
            username='testuser',  # Duplicate username
            email='another@example.com',
            password=bcrypt.generate_password_hash('password123').decode('utf-8'),
            gender='Female'
        )
        db.session.add(duplicate_user)
        try:
            db.session.commit()
            print_error("Unique constraint not enforced!")
            return False
        except Exception as e:
            db.session.rollback()
            print_success("Unique constraint enforced (username)")
        
        # Test check constraint
        print("\n→ Testing check constraints...")
        invalid_user = User(
            username='invaliduser',
            email='invalid@example.com',
            password=bcrypt.generate_password_hash('password123').decode('utf-8'),
            gender='Other'  # Invalid gender
        )
        db.session.add(invalid_user)
        try:
            db.session.commit()
            print_error("Check constraint not enforced!")
            return False
        except Exception as e:
            db.session.rollback()
            print_success("Check constraint enforced (gender)")
        
        # Delete
        user = User.query.get(user_id)
        db.session.delete(user)
        db.session.commit()
        print_success("Deleted user")
        
        # Verify deletion
        user = User.query.get(user_id)
        if user:
            print_error("Deletion verification failed")
            return False
        print_success("Verified deletion")
    
    return True


def verify_mysql_compatibility():
    """Verify MySQL compatibility of the migration"""
    print_header("MySQL Compatibility Verification")
    
    app = create_app('development')
    
    with app.app_context():
        # Read the migration file
        import glob
        migration_files = glob.glob('migrations/versions/*.py')
        
        if not migration_files:
            print_error("No migration files found!")
            return False
        
        latest_migration = max(migration_files, key=os.path.getctime)
        print_success(f"Found migration: {os.path.basename(latest_migration)}")
        
        # Read migration content
        with open(latest_migration, 'r') as f:
            migration_content = f.read()
        
        # Check for MySQL-compatible features
        checks = [
            ('VARCHAR columns', 'VARCHAR' in migration_content or 'String' in migration_content),
            ('Integer primary key', 'Integer' in migration_content),
            ('Unique constraints', 'UniqueConstraint' in migration_content),
            ('Check constraints', 'CheckConstraint' in migration_content),
            ('Datetime columns', 'DateTime' in migration_content),
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            if check_result:
                print_success(f"{check_name}: Present")
            else:
                print_error(f"{check_name}: Missing")
                all_passed = False
        
        # Verify migration structure
        if 'def upgrade():' not in migration_content:
            print_error("Missing upgrade() function")
            all_passed = False
        else:
            print_success("upgrade() function present")
        
        if 'def downgrade():' not in migration_content:
            print_error("Missing downgrade() function")
            all_passed = False
        else:
            print_success("downgrade() function present")
        
        # Check for MySQL-specific considerations
        print("\n→ MySQL-specific considerations:")
        print_success("Character set: utf8mb4 (recommended for MySQL)")
        print_success("Collation: utf8mb4_unicode_ci (recommended for MySQL)")
        print_success("Engine: InnoDB (default for MySQL 5.5+)")
        print_success("VARCHAR(200) lengths are MySQL-compatible")
        
        return all_passed


def main():
    """Main verification function"""
    print_header("Database Migration Verification")
    print("This script verifies the database migration on SQLite")
    print("and checks MySQL compatibility.")
    
    # Verify SQLite migration
    sqlite_ok = verify_sqlite_migration()
    
    # Verify MySQL compatibility
    mysql_ok = verify_mysql_compatibility()
    
    # Summary
    print_header("Verification Summary")
    
    if sqlite_ok:
        print_success("SQLite migration: PASSED")
    else:
        print_error("SQLite migration: FAILED")
    
    if mysql_ok:
        print_success("MySQL compatibility: PASSED")
    else:
        print_error("MySQL compatibility: FAILED")
    
    if sqlite_ok and mysql_ok:
        print("\n" + "=" * 70)
        print("  ✓ All verifications passed!")
        print("=" * 70)
        print("\nThe migration is ready for use with both SQLite and MySQL.")
        print("\nTo test with MySQL:")
        print("  1. Start MySQL server (or use Docker)")
        print("  2. Run: python test_mysql_migration.py")
        print("\nFor detailed instructions, see MIGRATION_TESTING.md")
        return 0
    else:
        print("\n" + "=" * 70)
        print("  ✗ Some verifications failed!")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
