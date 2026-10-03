# SQL Injection Prevention Project - Setup Guide

## Overview
This project demonstrates SQL injection vulnerabilities and their fixes using PHP and MySQL. It includes a complete user management system with authentication, CRUD operations, and comprehensive security testing.

## Prerequisites

1. **XAMPP** (or similar LAMP/WAMP stack)
   - Apache Web Server
   - MySQL Database
   - PHP 7.4 or higher

2. **Composer** (for PHPUnit testing)
   - Download from: https://getcomposer.org/

## Installation Steps

### Step 1: Install XAMPP
1. Download XAMPP from https://www.apachefriends.org/
2. Install XAMPP to `C:\xampp` (default location)
3. Start Apache and MySQL from XAMPP Control Panel

### Step 2: Setup Database
1. Open phpMyAdmin: http://localhost/phpmyadmin
2. Import the database:
   - Click "Import" tab
   - Choose file: `Database/127_0_0_1.sql`
   - Click "Go"
3. Verify `user_db` database is created with `users` table
4. Default test users:
   - Username: `admin`, Password: `admin123`
   - Username: `shashank`, Password: `shashank123`

### Step 3: Configure Database Connection
1. Open `connect.php`
2. Verify database credentials:
   ```php
   $hostname = "localhost";
   $username = "root";
   $password = "";  // Default XAMPP has no password
   $dbname = "user_db";
   ```

### Step 4: Install Composer Dependencies (for testing)
1. Open Command Prompt in project directory
2. Run: `composer install`
3. This installs PHPUnit and dependencies

### Step 5: Run Password Migration
**IMPORTANT**: Run this ONCE to hash existing plain text passwords
```bash
php migrate_passwords.php
```

Expected output:
```
✓ Database connection established
Starting password migration...
User #1 (admin): Password hashed successfully - MIGRATED
User #2 (shashank): Password hashed successfully - MIGRATED
✓ SUCCESS: All plain text passwords have been migrated to bcrypt hashes.
```

### Step 6: Deploy to Web Server
1. Copy project folder to: `C:\xampp\htdocs\SQLi_Injection`
2. Access application: http://localhost/SQLi_Injection/index.html

## Running the Application

### Login Page
- URL: http://localhost/SQLi_Injection/index.html
- Test credentials:
  - Username: `admin`, Password: `admin123`
  - Username: `shashank`, Password: `shashank123`

### Admin Page
- After successful login, you'll be redirected to `admin_page.html`
- Options:
  - View all users
  - Add new user
  - Update user
  - Delete user

### User Management
- **View Users**: http://localhost/SQLi_Injection/show_users.php
- **Add User**: http://localhost/SQLi_Injection/new_users.html
- **Update User**: Click "Update" button in user list
- **Delete User**: Click "Delete" button in user list

## Running Tests

### Bug Condition Exploration Tests
Tests that verify SQL injection vulnerabilities are fixed:
```bash
# Windows
run_tests.bat

# Or manually
vendor\bin\phpunit tests\BugConditionExplorationTest.php
```

### Preservation Property Tests
Tests that verify legitimate functionality still works:
```bash
# Windows
run_preservation_tests.bat

# Or manually
vendor\bin\phpunit tests\PreservationPropertyTest.php
```

### Run All Tests
```bash
vendor\bin\phpunit
```

## Security Features Implemented

### 1. SQL Injection Prevention
- ✅ Prepared statements with parameter binding
- ✅ Input validation and sanitization
- ✅ No direct SQL query concatenation

### 2. Password Security
- ✅ Passwords hashed with bcrypt (PASSWORD_DEFAULT)
- ✅ Password verification with `password_verify()`
- ✅ Passwords not displayed in user interface
- ✅ Migration script for existing plain text passwords

### 3. Error Handling
- ✅ Secure error logging (errors logged to file)
- ✅ Generic user-facing error messages
- ✅ No database schema exposure

### 4. Input Validation
- ✅ Email format validation
- ✅ Length restrictions (max 200 characters)
- ✅ Gender value validation
- ✅ ID parameter validation (numeric, positive)

## Project Structure

```
SQLi_Injection/
├── index.html              # Login page
├── admin_page.html         # Admin dashboard
├── new_users.html          # Add new user form
├── connect.php             # Database connection
├── connection.php          # Login authentication (SECURE)
├── new_user.php            # Create user (SECURE)
├── update.php              # Update user (SECURE)
├── delete.php              # Delete user (SECURE)
├── show_users.php          # Display users (SECURE)
├── migrate_passwords.php   # Password migration script
├── Database/
│   └── 127_0_0_1.sql      # Database schema and data
├── tests/
│   ├── BugConditionExplorationTest.php    # Security tests
│   ├── PreservationPropertyTest.php       # Functionality tests
│   └── README.md          # Testing documentation
├── composer.json           # PHP dependencies
├── phpunit.xml            # PHPUnit configuration
└── SETUP_GUIDE.md         # This file
```

## Troubleshooting

### Database Connection Failed
- Verify MySQL is running in XAMPP Control Panel
- Check database credentials in `connect.php`
- Ensure `user_db` database exists

### Login Not Working
- Run password migration script: `php migrate_passwords.php`
- Verify users exist in database
- Check Apache error logs: `C:\xampp\apache\logs\error.log`

### Tests Failing
- Run `composer install` to install PHPUnit
- Verify database is set up correctly
- Check that migration script has been run

### Page Not Found (404)
- Verify project is in `C:\xampp\htdocs\SQLi_Injection`
- Check Apache is running
- Use correct URL: http://localhost/SQLi_Injection/index.html

## Testing SQL Injection Prevention

### Before Fix (Vulnerable Code)
If you want to see how SQL injection works, you would need the original vulnerable code where:
- Username: `admin' OR '1'='1` would bypass authentication
- Malicious SQL in forms would execute

### After Fix (Current Secure Code)
- All SQL injection attempts are blocked
- Prepared statements prevent malicious SQL execution
- Input validation rejects invalid data

## Next Steps

1. ✅ Database setup complete
2. ✅ Security fixes implemented
3. ✅ Migration script ready
4. ⏳ Run migration script
5. ⏳ Test application functionality
6. ⏳ Run security tests

## Support

For issues or questions:
1. Check error logs: `C:\xampp\apache\logs\error.log`
2. Review test output for specific failures
3. Verify all setup steps completed

## License

This is an educational project demonstrating SQL injection vulnerabilities and their fixes.

````