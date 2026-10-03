# Preservation Property Tests

## Overview

This directory contains preservation property tests for the SQL injection security fixes bugfix spec. These tests are designed to **PASS on unfixed code** to establish baseline behavior that must be preserved after implementing security fixes.

**IMPORTANT**: Test passes on unfixed code are the EXPECTED outcome. These tests capture legitimate user operations that must continue working after security fixes are applied.

## Test Coverage

The tests validate the following preservation requirements (Requirements 3.1-3.13):

### Authentication Preservation
1. **Authentication Success** - Valid credentials (admin/admin123) should authenticate and redirect to admin_page.html
2. **Authentication Failure** - Invalid credentials should fail and redirect to index.html with error

### CRUD Operations Preservation
3. **User Creation** - Create user with valid data should insert record and redirect to show_users.php
4. **User Update** - Update user with valid data should modify record and redirect to show_users.php
5. **User Deletion** - Delete user with valid ID should remove record and redirect to show_users.php

### Display Preservation
6. **User Display** - show_users.php should display user table with id, username, email, gender, operations (password column will be removed after fix)

### Connection Preservation
7. **Database Connection** - Connection with existing parameters (localhost, root, no password, user_db) should succeed

### Existing Users Preservation
8. **Test Users** - Existing test users (admin/admin123, shashank/shashank123) should authenticate successfully

### Full Lifecycle Preservation
9. **Multiple Operations** - Full user lifecycle (create → update → display → delete) should work correctly

## Requirements

- PHP 7.0 or higher
- MySQL/MariaDB database
- Database `user_db` must exist with `users` table
- Database connection: localhost, root user, no password

## Running the Tests

### Option 1: Direct PHP Execution (Recommended)

```bash
php tests/run_preservation_tests.php
```

### Option 2: Using PHPUnit (if installed)

```bash
composer install
vendor/bin/phpunit tests/PreservationPropertyTest.php
```

### Option 3: Windows Batch Script

```cmd
run_preservation_tests.bat
```

## Expected Results

### On UNFIXED Code (Current State - Task 2)
- **Expected**: All tests should PASS
- **Meaning**: Baseline behavior is captured correctly
- **Action**: Proceed to implement security fixes (Task 3)

### On FIXED Code (After Task 3)
- **Expected**: All tests should STILL PASS
- **Meaning**: Security fixes did not break existing functionality (no regressions)
- **Action**: Verify bug condition tests also pass (vulnerabilities fixed)

## Test Output

The test runner provides detailed output including:
- Test name and description
- Pass/Fail status with ✓ or ✗ indicators
- Detailed failure messages if any
- Summary of total tests run, passed, and failed

Example output:
```
╔════════════════════════════════════════════════════════════════════════════════╗
║                    PRESERVATION PROPERTY TESTS                                 ║
║                                                                                ║
║  IMPORTANT: These tests MUST PASS on unfixed code                             ║
║  They capture legitimate user operations that must be preserved               ║
╚════════════════════════════════════════════════════════════════════════════════╝

================================================================================
Test 1: Authentication Success with Valid Credentials
================================================================================
✓ PASSED: Authentication with valid credentials

...

╔════════════════════════════════════════════════════════════════════════════════╗
║                              TEST SUMMARY                                      ║
╚════════════════════════════════════════════════════════════════════════════════╝

Total Tests Run: 9
Tests Passed: 9
Tests Failed: 0

╔════════════════════════════════════════════════════════════════════════════════╗
║                          ALL TESTS PASSED!                                     ║
║                                                                                ║
║  SUCCESS: Baseline behavior captured successfully.                            ║
║  These tests establish the preservation requirements for security fixes.      ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

## Test Methodology

These tests follow the **observation-first preservation** methodology:

1. **Observe Behavior on Unfixed Code**: Run tests on vulnerable code to capture current behavior
2. **Encode as Property Tests**: Write tests that encode the observed legitimate operations
3. **Establish Baseline**: Tests pass on unfixed code, establishing what must be preserved
4. **Implement Security Fixes**: Apply security fixes (Task 3)
5. **Verify Preservation**: Re-run tests to ensure they still pass (no regressions)
6. **Verify Bug Fixes**: Ensure bug condition tests now pass (vulnerabilities fixed)

## Files

- `PreservationPropertyTest.php` - PHPUnit test class (requires PHPUnit)
- `run_preservation_tests.php` - Standalone test runner (no dependencies)
- `PRESERVATION_README.md` - This documentation file

## Notes

- Tests create and clean up temporary test data in the database
- All test data is cleaned up after each test runs
- Tests are designed to be non-destructive to existing data
- Tests verify the same SQL query patterns used in the actual PHP files
- After security fixes, some behaviors will change (e.g., passwords hashed instead of plain text), but the functional outcomes (authentication success/failure, CRUD operations) must remain the same

## Property-Based Testing Approach

While these tests use specific examples, they follow property-based testing principles:

- **Properties**: Each test encodes a property that must hold (e.g., "valid credentials authenticate successfully")
- **Multiple Inputs**: Tests use various valid inputs (different usernames, emails, timestamps)
- **Invariants**: Tests verify invariants that must hold across all legitimate operations
- **Generators**: Tests generate test data dynamically (using timestamps for uniqueness)

This approach provides stronger guarantees than simple unit tests because it verifies behavior across a range of inputs rather than just specific hardcoded examples.

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

### "Admin user not found"
- Ensure the database has been populated with test users
- Check that the users table has at least the admin user with password admin123

## Next Steps

After running these tests on unfixed code:

1. **Verify All Tests Pass**: Ensure baseline behavior is captured correctly
2. **Document Baseline**: Record the expected behavior for each test
3. **Proceed to Task 3**: Implement security fixes
4. **Re-run Preservation Tests**: Verify all tests still pass (no regressions)
5. **Re-run Bug Condition Tests**: Verify all bug condition tests now pass (vulnerabilities fixed)

## Comparison with Bug Condition Tests

| Aspect | Bug Condition Tests | Preservation Tests |
|--------|--------------------|--------------------|
| **Purpose** | Demonstrate vulnerabilities exist | Capture legitimate operations |
| **Expected on Unfixed** | FAIL (vulnerabilities exist) | PASS (baseline behavior) |
| **Expected on Fixed** | PASS (vulnerabilities fixed) | PASS (no regressions) |
| **Test Inputs** | Malicious payloads | Valid user data |
| **Validates** | Security requirements (2.x) | Preservation requirements (3.x) |
| **Methodology** | Bug condition exploration | Observation-first preservation |

Both test suites are essential:
- **Bug Condition Tests** prove the vulnerabilities are fixed
- **Preservation Tests** prove the fixes didn't break existing functionality

## Important Notes

✓ **These tests are designed to PASS on unfixed code**  
✓ **Test passes CONFIRM baseline behavior is captured**  
✓ **Tests must STILL PASS after security fixes**  
✓ **Run on local development environment only**  
✓ **Never run on production systems**

---

**Preservation Testing Complete** - Baseline behavior established!


````