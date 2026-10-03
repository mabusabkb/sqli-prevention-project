# Test Setup Instructions

## Prerequisites

Before running the bug condition exploration tests, ensure the following prerequisites are met:

### 1. PHP Installation

**Required Version**: PHP 7.0 or higher

**Check if PHP is installed**:
```bash
php --version
```

**If PHP is not installed**:

- **Windows**: Download from [https://windows.php.net/download/](https://windows.php.net/download/)
  - Download the "Thread Safe" ZIP package
  - Extract to `C:\php`
  - Add `C:\php` to your system PATH
  - Copy `php.ini-development` to `php.ini`
  - Enable mysqli extension: Uncomment `;extension=mysqli` in php.ini

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update
  sudo apt install php php-mysqli
  ```

- **Linux (CentOS/RHEL)**:
  ```bash
  sudo yum install php php-mysqli
  ```

- **macOS**:
  ```bash
  brew install php
  ```

### 2. MySQL/MariaDB Installation

**Required**: MySQL 5.7+ or MariaDB 10.0+

**Check if MySQL is installed**:
```bash
mysql --version
```

**If MySQL is not installed**:

- **Windows**: Download from [https://dev.mysql.com/downloads/installer/](https://dev.mysql.com/downloads/installer/)
  - Use MySQL Installer
  - Install MySQL Server
  - Set root password (or leave empty for testing)

- **Linux (Ubuntu/Debian)**:
  ```bash
  sudo apt update
  sudo apt install mysql-server
  sudo mysql_secure_installation
  ```

- **Linux (CentOS/RHEL)**:
  ```bash
  sudo yum install mysql-server
  sudo systemctl start mysqld
  sudo mysql_secure_installation
  ```

- **macOS**:
  ```bash
  brew install mysql
  brew services start mysql
  ```

### 3. Database Setup

**Step 1: Start MySQL Service**

- **Windows**: MySQL should start automatically, or use Services panel
- **Linux**: `sudo systemctl start mysql` or `sudo service mysql start`
- **macOS**: `brew services start mysql`

**Step 2: Create Database and Import Schema**

```bash
# Connect to MySQL
mysql -u root -p

# Create database (if not exists)
CREATE DATABASE IF NOT EXISTS user_db;

# Exit MySQL
exit;

# Import the database schema
mysql -u root -p user_db < Database/127_0_0_1.sql
```

**Step 3: Verify Database Setup**

```bash
mysql -u root -p user_db -e "SELECT * FROM users;"
```

Expected output:
```
+----+----------+---------------------+-------------+--------+
| id | username | email               | password    | gender |
+----+----------+---------------------+-------------+--------+
|  1 | admin    | admin123@gmail.com  | admin123    | Male   |
|  2 | shashank | shashankghodke...   | shashank123 | Male   |
+----+----------+---------------------+-------------+--------+
```

### 4. PHP Configuration

**Enable mysqli extension**:

1. Locate your `php.ini` file:
   ```bash
   php --ini
   ```

2. Open `php.ini` in a text editor

3. Find and uncomment (remove `;` from) the following line:
   ```ini
   ;extension=mysqli
   ```
   Change to:
   ```ini
   extension=mysqli
   ```

4. Save and restart your web server (if applicable)

5. Verify mysqli is enabled:
   ```bash
   php -m | grep mysqli
   ```
   Should output: `mysqli`

## Running the Tests

Once all prerequisites are met, you can run the tests:

### Option 1: Direct PHP Execution (Recommended)

```bash
php tests/run_bug_exploration_tests.php
```

### Option 2: Windows Batch Script

```cmd
run_tests.bat
```

### Option 3: PHPUnit (Optional)

If you want to use PHPUnit:

```bash
# Install Composer first (https://getcomposer.org/download/)
composer install

# Run tests
vendor/bin/phpunit tests/BugConditionExplorationTest.php
```

## Troubleshooting

### Error: "Database connection failed"

**Cause**: Cannot connect to MySQL database

**Solutions**:
1. Verify MySQL is running: `sudo systemctl status mysql` (Linux) or check Services (Windows)
2. Check connection credentials in test files (localhost, root, no password)
3. Verify database `user_db` exists: `mysql -u root -p -e "SHOW DATABASES;"`
4. Check MySQL is listening on localhost:3306: `netstat -an | grep 3306`

### Error: "Table 'user_db.users' doesn't exist"

**Cause**: Database schema not imported

**Solution**:
```bash
mysql -u root -p user_db < Database/127_0_0_1.sql
```

### Error: "Call to undefined function mysqli_connect()"

**Cause**: mysqli extension not enabled

**Solution**:
1. Edit `php.ini` and uncomment `extension=mysqli`
2. Restart web server or PHP-FPM
3. Verify: `php -m | grep mysqli`

### Error: "Access denied for user 'root'@'localhost'"

**Cause**: MySQL root password is set but tests expect no password

**Solutions**:
1. **Option A**: Update test files to use your MySQL password
   - Edit `tests/run_bug_exploration_tests.php`
   - Change `$db_pass = "";` to `$db_pass = "your_password";`

2. **Option B**: Reset MySQL root password to empty (not recommended for production)
   ```bash
   mysql -u root -p
   ALTER USER 'root'@'localhost' IDENTIFIED BY '';
   FLUSH PRIVILEGES;
   ```

### Error: "PHP is not recognized as an internal or external command"

**Cause**: PHP not in system PATH

**Solution (Windows)**:
1. Find PHP installation directory (e.g., `C:\php`)
2. Add to PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Edit "Path" variable
   - Add PHP directory
   - Restart command prompt

**Solution (Linux/Mac)**:
```bash
# Add to ~/.bashrc or ~/.zshrc
export PATH="/path/to/php:$PATH"
source ~/.bashrc
```

## Test Environment Verification

Run this verification script to check your environment:

```bash
php -r "
echo 'PHP Version: ' . PHP_VERSION . PHP_EOL;
echo 'mysqli extension: ' . (extension_loaded('mysqli') ? 'Enabled' : 'DISABLED') . PHP_EOL;
\$conn = @mysqli_connect('localhost', 'root', '', 'user_db');
echo 'Database connection: ' . (\$conn ? 'Success' : 'FAILED: ' . mysqli_connect_error()) . PHP_EOL;
if (\$conn) {
    \$result = mysqli_query(\$conn, 'SELECT COUNT(*) as count FROM users');
    \$row = mysqli_fetch_assoc(\$result);
    echo 'Users table: ' . (\$row ? 'Found (' . \$row['count'] . ' users)' : 'NOT FOUND') . PHP_EOL;
    mysqli_close(\$conn);
}
"
```

Expected output:
```
PHP Version: 7.4.30 (or higher)
mysqli extension: Enabled
Database connection: Success
Users table: Found (2 users)
```

## Next Steps

Once your environment is set up and verified:

1. ✓ **Prerequisites Met** - PHP, MySQL, mysqli extension
2. ✓ **Database Created** - user_db with users table
3. ✓ **Test Files Ready** - tests/run_bug_exploration_tests.php
4. **Run Tests** - Execute bug condition exploration tests
5. **Review Results** - Check counterexamples found
6. **Document Findings** - Update COUNTEREXAMPLES.md with actual results

## Support

If you encounter issues not covered in this guide:

1. Check PHP error logs: `php -i | grep error_log`
2. Check MySQL error logs: `/var/log/mysql/error.log` (Linux) or MySQL data directory (Windows)
3. Enable PHP error reporting in test files:
   ```php
   error_reporting(E_ALL);
   ini_set('display_errors', 1);
   ```
4. Run tests with verbose output to see detailed error messages

## Security Note

These tests are designed to run on a **local development environment only**. Do not run these tests on production systems or publicly accessible servers, as they:

- Attempt SQL injection attacks
- Create and delete test data
- May expose security vulnerabilities
- Could impact database performance

Always use an isolated test environment for security testing.

````