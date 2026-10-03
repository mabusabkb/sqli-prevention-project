# Testing Quick Start Guide

## Bug Condition Exploration Tests - Quick Reference

This guide provides quick commands to run the bug condition exploration tests for the SQL injection security fixes.

## Prerequisites Check

```bash
# Check PHP is installed
php --version

# Check MySQL is running
mysql -u root -p -e "SELECT 1;"

# Verify database exists
mysql -u root -p -e "USE user_db; SELECT COUNT(*) FROM users;"
```

## Run Tests

### Windows

```cmd
run_tests.bat
```

### Linux/Mac

```bash
php tests/run_bug_exploration_tests.php
```

## Expected Output

### On UNFIXED Code (Current)

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                    BUG CONDITION EXPLORATION TESTS                             ║
║                                                                                ║
║  CRITICAL: These tests MUST FAIL on unfixed code                              ║
║  Failure confirms the vulnerabilities exist                                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

================================================================================
Running Test 1: SQL Injection - Login Bypass (connection.php)
================================================================================
✗ FAILED: SQL injection bypassed authentication (2 rows returned, expected 0)

...

╔════════════════════════════════════════════════════════════════════════════════╗
║                              TEST SUMMARY                                      ║
╚════════════════════════════════════════════════════════════════════════════════╝

Total Tests Run: 10
Tests Passed: 0
Tests Failed: 10

╔════════════════════════════════════════════════════════════════════════════════╗
║                           COUNTEREXAMPLES FOUND                                ║
║                                                                                ║
║  These failures CONFIRM the vulnerabilities exist in the unfixed code.        ║
║  This is the EXPECTED outcome for bug condition exploration tests.            ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

**This is CORRECT** - Failures confirm vulnerabilities exist!

### On FIXED Code (After Task 3)

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                              TEST SUMMARY                                      ║
╚════════════════════════════════════════════════════════════════════════════════╝

Total Tests Run: 10
Tests Passed: 10
Tests Failed: 0
```

**This is SUCCESS** - All vulnerabilities fixed!

## Troubleshooting

### "PHP is not recognized"

**Windows**:
1. Download PHP from https://windows.php.net/download/
2. Extract to C:\php
3. Add C:\php to PATH
4. Restart command prompt

**Linux/Mac**:
```bash
# Ubuntu/Debian
sudo apt install php php-mysqli

# CentOS/RHEL
sudo yum install php php-mysqli

# macOS
brew install php
```

### "Database connection failed"

```bash
# Start MySQL
# Windows: Check Services panel
# Linux: sudo systemctl start mysql
# Mac: brew services start mysql

# Import database
mysql -u root -p user_db < Database/127_0_0_1.sql
```

### "mysqli extension not loaded"

Edit `php.ini` and uncomment:
```ini
extension=mysqli
```

Find php.ini location:
```bash
php --ini
```

## What Tests Check

| # | Test | Vulnerability | Expected on Unfixed |
|---|------|---------------|---------------------|
| 1 | Login Bypass | SQL Injection | ✗ FAIL |
| 2 | New User Creation | SQL Injection | ✗ FAIL |
| 3 | User Update | SQL Injection | ✗ FAIL |
| 4 | User Deletion | SQL Injection | ✗ FAIL |
| 5 | Password Storage | Plain Text | ✗ FAIL |
| 6 | Password Display | Plain Text | ✗ FAIL |
| 7 | Error Disclosure (delete) | Info Leak | ✗ FAIL |
| 8 | Error Disclosure (connect) | Info Leak | ✗ FAIL |
| 9 | Email Validation | Missing | ✗ FAIL |
| 10 | Length Validation | Missing | ✗ FAIL |

## Next Steps

1. ✓ Run tests on unfixed code
2. ✓ Document counterexamples found
3. → Proceed to Task 2 (preservation tests)
4. → Proceed to Task 3 (implement fixes)
5. → Re-run tests to verify fixes

## Documentation

- **Full Setup**: `tests/SETUP.md`
- **Test Details**: `tests/README.md`
- **Counterexamples**: `tests/COUNTEREXAMPLES.md`
- **Task Completion**: `tests/TASK1_COMPLETION.md`

## Support

If you encounter issues:

1. Check `tests/SETUP.md` for detailed troubleshooting
2. Verify environment with:
   ```bash
   php -r "echo 'PHP: ' . PHP_VERSION . PHP_EOL; echo 'mysqli: ' . (extension_loaded('mysqli') ? 'OK' : 'MISSING') . PHP_EOL;"
   ```
3. Check MySQL connection:
   ```bash
   mysql -u root -p user_db -e "SELECT * FROM users;"
   ```

## Important Notes

⚠️ **These tests are designed to FAIL on unfixed code**  
⚠️ **Test failures CONFIRM vulnerabilities exist**  
⚠️ **DO NOT fix tests or code during Task 1**  
⚠️ **Run on local development environment only**  
⚠️ **Never run on production systems**

---

**Quick Start Complete** - You're ready to run the tests!

````