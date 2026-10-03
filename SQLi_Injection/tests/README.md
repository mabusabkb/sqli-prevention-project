# Bug Condition Exploration Tests

## Overview

This directory contains bug condition exploration tests for the SQL injection security fixes bugfix spec. These tests are designed to **FAIL on unfixed code** to demonstrate that the security vulnerabilities exist.

**CRITICAL**: Test failures on unfixed code are the EXPECTED outcome. Do NOT attempt to fix the tests or the code when they fail during this phase.

## Test Coverage

The tests validate the following security vulnerabilities (Requirements 1.1-1.15):

### SQL Injection Vulnerabilities
1. **Login Bypass (connection.php)** - Tests if SQL injection can bypass authentication
2. **New User Creation (new_user.php)** - Tests if SQL injection can manipulate user creation
3. **User Update (update.php)** - Tests if SQL injection can modify unintended records
4. **User Deletion (delete.php)** - Tests if SQL injection can delete multiple/all records

### Password Security Vulnerabilities
5. **Plain Text Password Storage** - Tests if passwords are stored without hashing
6. **Plain Text Password Display** - Tests if passwords are visible in show_users.php

### Error Disclosure Vulnerabilities
7. **Error Disclosure in delete.php** - Tests if detailed MySQL errors are exposed
8. **Error Disclosure in connect.php** - Tests if connection details are exposed

### Input Validation Vulnerabilities
9. **Missing Email Validation** - Tests if invalid email formats are accepted
10. **Missing Length Validation** - Tests if excessive length input is accepted

## Requirements

- PHP 7.0 or higher
- MySQL/MariaDB database
- Database `user_db` must exist with `users` table
- Database connection: localhost, root user, no password

## Running the Tests

### Option 1: Direct PHP Execution (Recommended)

```bash
php tests/run_bug_exploration_tests.php
```

### Option 2: Using PHPUnit (if installed)

```bash
composer install
vendor/bin/phpunit tests/BugConditionExplorationTest.php
```

### Option 3: Windows Batch Script

```cmd
run_tests.bat
```

## Expected Results

### On UNFIXED Code (Current State)
- **Expected**: Most or all tests should FAIL
- **Meaning**: Vulnerabilities are confirmed to exist
- **Action**: Document the counterexamples and proceed to implement fixes

### On FIXED Code (After Task 3)
- **Expected**: All tests should PASS
- **Meaning**: Security vulnerabilities have been successfully fixed
- **Action**: Verify preservation tests still pass (no regressions)

## Test Output

The test runner provides detailed output including:
- Test name and description
- Pass/Fail status with ✓ or ✗ indicators
- Detailed failure messages with counterexamples
- Summary of total tests run, passed, and failed
- List of all counterexamples found

Example output:
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
║                           COUNTEREXAMPLES FOUND                                ║
║                                                                                ║
║  These failures CONFIRM the vulnerabilities exist in the unfixed code.        ║
║  This is the EXPECTED outcome for bug condition exploration tests.            ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

## Test Methodology

These tests follow the **bug condition exploration** methodology:

1. **Encode Expected Secure Behavior**: Each test encodes what the FIXED code should do
2. **Run on Unfixed Code**: Tests are run on vulnerable code first
3. **Document Counterexamples**: Failures demonstrate the vulnerabilities exist
4. **Implement Fixes**: Security fixes are implemented (Task 3)
5. **Verify Fixes**: Same tests are re-run and should now pass

## Files

- `BugConditionExplorationTest.php` - PHPUnit test class (requires PHPUnit)
- `run_bug_exploration_tests.php` - Standalone test runner (no dependencies)
- `README.md` - This documentation file

## Notes

- Tests create and clean up temporary test data in the database
- Tests may create temporary PHP files for error disclosure testing
- All test data is cleaned up after each test runs
- Tests are designed to be non-destructive to existing data
- Some tests may temporarily close database connections to simulate errors

## Troubleshooting

### "Database connection failed"
- Ensure MySQL/MariaDB is running
- Verify database `user_db` exists
- Check connection credentials (localhost, root, no password)

### "Table 'user_db.users' doesn't exist"
- Run the database setup script: `mysql -u root user_db < Database/127_0_0_1.sql`

### "PHP not found"
- Ensure PHP is installed and in your system PATH
- On Windows: Add PHP installation directory to PATH environment variable
- On Linux/Mac: Install PHP via package manager (apt, yum, brew)

## Next Steps

After running these tests on unfixed code:

1. **Document Counterexamples**: Record which tests failed and why
2. **Proceed to Task 2**: Write preservation property tests
3. **Proceed to Task 3**: Implement security fixes
4. **Re-run Tests**: Verify all bug condition tests now pass
5. **Verify Preservation**: Ensure preservation tests still pass (no regressions)

````