# SQL Injection Prevention Project

A comprehensive PHP web application demonstrating SQL injection vulnerabilities and their security fixes, complete with property-based testing.

## 🎯 Project Overview

This project showcases:
- **SQL Injection Vulnerabilities** and how they work
- **Security Fixes** using prepared statements and password hashing
- **Property-Based Testing** to verify security and functionality
- **Complete User Management System** with CRUD operations

## 🚀 Quick Start

### Prerequisites
- XAMPP (Apache + MySQL + PHP 7.4+)
- Composer (for testing)

### Installation (3 Steps)

1. **Setup Database**
   ```bash
   # Import database in phpMyAdmin
   # File: Database/127_0_0_1.sql
   ```

2. **Run Migration Script**
   ```bash
   php migrate_passwords.php
   ```

3. **Open Application**
   ```
   http://localhost/SQLi_Injection/index.html
   ```

### Or Use Quick Start Menu
```bash
QUICKSTART.bat
```

## 📋 Features

### Security Features ✅
- ✅ **SQL Injection Prevention** - Prepared statements with parameter binding
- ✅ **Password Security** - Bcrypt hashing with `password_hash()`
- ✅ **Input Validation** - Email, length, and format validation
- ✅ **Secure Error Handling** - No sensitive information exposure
- ✅ **XSS Prevention** - Output escaping with `htmlspecialchars()`

### Application Features
- 🔐 User Authentication (Login/Logout)
- 👤 User Management (Create, Read, Update, Delete)
- 📊 User Dashboard
- 🔒 Password Migration Tool

## 🧪 Testing

### Run All Tests
```bash
vendor\bin\phpunit
```

### Security Tests (Bug Condition Exploration)
```bash
run_tests.bat
```
Tests that verify SQL injection attacks are blocked.

### Functionality Tests (Preservation Properties)
```bash
run_preservation_tests.bat
```
Tests that verify legitimate operations still work.

## 📁 Project Structure

```
SQLi_Injection/
├── 📄 index.html              # Login page
├── 📄 admin_page.html         # Admin dashboard
├── 📄 connection.php          # Secure authentication
├── 📄 new_user.php            # Secure user creation
├── 📄 update.php              # Secure user update
├── 📄 delete.php              # Secure user deletion
├── 📄 show_users.php          # Secure user display
├── 📄 migrate_passwords.php   # Password migration
├── 📂 Database/
│   └── 127_0_0_1.sql         # Database schema
├── 📂 tests/
│   ├── BugConditionExplorationTest.php
│   └── PreservationPropertyTest.php
└── 📄 SETUP_GUIDE.md          # Detailed setup instructions
```

## 🔑 Default Test Users

After running migration script:
- **Username:** `admin` | **Password:** `admin123`
- **Username:** `shashank` | **Password:** `shashank123`

## 📖 Documentation

- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Complete installation and configuration guide
- **[TESTING_QUICKSTART.md](TESTING_QUICKSTART.md)** - Testing guide
- **[tests/README.md](tests/README.md)** - Test documentation

## 🛡️ Security Comparison

### Before (Vulnerable)
```php
// ❌ VULNERABLE - Direct SQL concatenation
$sql = "SELECT * FROM users WHERE username='$uname' AND password='$pass'";
$result = mysqli_query($conn, $sql);
```

**Attack:** Username: `admin' OR '1'='1` bypasses authentication!

### After (Secure)
```php
// ✅ SECURE - Prepared statement
$stmt = mysqli_prepare($conn, "SELECT * FROM users WHERE username = ?");
mysqli_stmt_bind_param($stmt, "s", $uname);
mysqli_stmt_execute($stmt);
```

**Result:** SQL injection attempts are blocked!

## 🎓 Educational Value

This project demonstrates:
1. **How SQL Injection Works** - Understanding the vulnerability
2. **How to Fix It** - Implementing prepared statements
3. **How to Test It** - Property-based testing methodology
4. **Best Practices** - Secure coding patterns

## 🔧 Troubleshooting

### Login Not Working?
```bash
# Run password migration
php migrate_passwords.php
```

### Database Connection Failed?
- Check XAMPP MySQL is running
- Verify credentials in `connect.php`

### Tests Failing?
```bash
# Install dependencies
composer install
```

## 📊 Test Coverage

- ✅ SQL Injection Prevention (10 test cases)
- ✅ Password Security (3 test cases)
- ✅ Input Validation (5 test cases)
- ✅ Error Handling (2 test cases)
- ✅ Functional Preservation (8 test cases)

## 🎯 Learning Objectives

After completing this project, you will understand:
- How SQL injection vulnerabilities work
- How to prevent SQL injection with prepared statements
- How to implement secure password storage
- How to write property-based tests for security
- How to validate and sanitize user input

## 📝 License

Educational project for learning SQL injection prevention.

## 🤝 Contributing

This is an educational project. Feel free to:
- Report issues
- Suggest improvements
- Add more test cases
- Enhance documentation

## 📞 Support

For help:
1. Check [SETUP_GUIDE.md](SETUP_GUIDE.md)
2. Review test output
3. Check Apache error logs

---

**⚠️ IMPORTANT:** This project is for educational purposes. Never deploy vulnerable code to production!

**✅ Current Status:** All security fixes implemented and tested.

````