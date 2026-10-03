# Running All Tests - Complete Guide

## Overview

This guide explains how to run both test suites for the SQL injection security fixes:

1. **Bug Condition Exploration Tests** (Task 1) - Should FAIL on unfixed code
2. **Preservation Property Tests** (Task 2) - Should PASS on unfixed code

## Quick Start

### Run All Tests (Windows)

```cmd
REM Run bug condition tests (should FAIL on unfixed code)
run_tests.bat

REM Run preservation tests (should PASS on unfixed code)
run_preservation_tests.bat
```

### Run All Tests (Linux/Mac)

```bash
# Run bug condition tests (should FAIL on unfixed code)
php tests/run_bug_exploration_tests.php

# Run preservation tests (should PASS on unfixed code)
php tests/run_preservation_tests.php
```

## Test Suites Comparison

| Aspect | Bug Condition Tests | Preservation Tests |
|--------|--------------------|--------------------|
| **File** | `tests/BugConditionExplorationTest.php` | `tests/PreservationPropertyTest.php` |
| **Runner** | `tests/run_bug_exploration_tests.php` | `tests/run_preservation_tests.php` |
| **Batch** | `run_tests.bat` | `run_preservation_tests.bat` |
| **Purpose** | Demonstrate vulnerabilities exist | Capture legitimate operations |
| **Test Count** | 10 tests | 9 tests |
| **Expected on Unfixed** | ✗ FAIL (vulnerabilities exist) | ✓ PASS (baseline behavior) |
| **Expected on Fixed** | ✓ PASS (vulnerabilities fixed) | ✓ PASS (no regressions) |
| **Test Inputs** | Malicious SQL injection payloads | Valid user data |
| **Validates** | Security requirements (1.x, 2.x) | Preservation requirements (3.x) |
| **Methodology** | Bug condition exploration | Observation-first preservation |

## Expected Results Timeline

### Phase 1: Before Fixes (Tasks 1-2)

**Bug Condition Tests**:
```
Total Tests Run: 10
Tests Passed: 0
Tests Failed: 10  ← EXPECTED (vulnerabilities exist)
```

**Preservation Tests**:
```
Total Tests Run: 9
Tests Passed: 9  ← EXPECTED (baseline captured)
Tests Failed: 0
```

### Phase 2: After Fixes (Task 3)

**Bug Condition Tests**:
```
Total Tests Run: 10
Tests Passed: 10  ← SUCCESS (vulnerabilities fixed)
Tests Failed: 0
```

**Preservation Tests**:
```
Total Tests Run: 9
Tests Passed: 9  ← SUCCESS (no regressions)
Tests Failed: 0
```

## Running Tests with PHPUnit

If you have PHPUnit installed via Composer:

```bash
# Install dependencies
composer install

# Run bug condition tests
vendor/bin/phpunit tests/BugConditionExplorationTest.php

# Run preservation tests
vendor/bin/phpunit tests/PreservationPropertyTest.php

# Run all tests
vendor/bin/phpunit tests/
```

## Test Execution Order

### Recommended Order for Task Execution

1. **Task 1**: Run bug condition tests on unfixed code
   ```cmd
   run_tests.bat
   ```
   - Expected: Tests FAIL (confirms vulnerabilities exist)
   - Document counterexamples found

2. **Task 2**: Run preservation tests on unfixed code
   ```cmd
   run_preservation_tests.bat
   ```
   - Expected: Tests PASS (captures baseline behavior)
   - Baseline established for regression prevention

3. **Task 3**: Implement security fixes
   - Fix connection.php (prepared statements, password verification)
   - Fix new_user.php (prepared statements, password hashing)
   - Fix update.php (prepared statements, password hashing)
   - Fix delete.php (prepared statements, secure error handling)
   - Fix show_users.php (remove password display, prepared statements)
   - Fix connect.php (secure error handling)
   - Create migration script for existing passwords

4. **Task 3.8**: Re-run bug condition tests on fixed code
   ```cmd
   run_tests.bat
   ```
   - Expected: Tests PASS (confirms vulnerabilities are fixed)

5. **Task 3.9**: Re-run preservation tests on fixed code
   ```cmd
   run_preservation_tests.bat
   ```
   - Expected: Tests PASS (confirms no regressions)

## Understanding Test Results

### Bug Condition Tests - What Each Test Checks

| # | Test | Checks For | Unfixed | Fixed |
|---|------|------------|---------|-------|
| 1 | SQL Injection - Login Bypass | Authentication bypass via SQL injection | ✗ FAIL | ✓ PASS |
| 2 | SQL Injection - New User | Data manipulation via SQL injection | ✗ FAIL | ✓ PASS |
| 3 | SQL Injection - Update | Record modification via SQL injection | ✗ FAIL | ✓ PASS |
| 4 | SQL Injection - Delete | Mass deletion via SQL injection | ✗ FAIL | ✓ PASS |
| 5 | Plain Text Password Storage | Passwords stored without hashing | ✗ FAIL | ✓ PASS |
| 6 | Plain Text Password Display | Passwords visible in UI | ✗ FAIL | ✓ PASS |
| 7 | Error Disclosure - Delete | Detailed MySQL errors exposed | ✗ FAIL | ✓ PASS |
| 8 | Error Disclosure - Connect | Connection details exposed | ✗ FAIL | ✓ PASS |
| 9 | Missing Email Validation | Invalid email formats accepted | ✗ FAIL | ✓ PASS |
| 10 | Missing Length Validation | Excessive length input accepted | ✗ FAIL | ✓ PASS |

### Preservation Tests - What Each Test Checks

| # | Test | Checks For | Unfixed | Fixed |
|---|------|------------|---------|-------|
| 1 | Authentication Success | Valid login works | ✓ PASS | ✓ PASS |
| 2 | Authentication Failure | Invalid login fails | ✓ PASS | ✓ PASS |
| 3 | User Creation | Create user works | ✓ PASS | ✓ PASS |
| 4 | User Update | Update user works | ✓ PASS | ✓ PASS |
| 5 | User Deletion | Delete user works | ✓ PASS | ✓ PASS |
| 6 | User Display | Display users works | ✓ PASS | ✓ PASS |
| 7 | Database Connection | Connection works | ✓ PASS | ✓ PASS |
| 8 | Existing Test Users | Admin/shashank authenticate | ✓ PASS | ✓ PASS |
| 9 | Full Lifecycle | Create→Update→Delete works | ✓ PASS | ✓ PASS |

## Troubleshooting

### Common Issues

#### "PHP is not recognized"
```cmd
# Windows: Add PHP to PATH
set PATH=%PATH%;C:\php

# Or download from: https://windows.php.net/download/
```

#### "Database connection failed"
```bash
# Check MySQL is running
# Windows: Check Services panel
# Linux: sudo systemctl status mysql

# Verify database exists
mysql -u root -p -e "USE user_db; SELECT COUNT(*) FROM users;"
```

#### "mysqli extension not loaded"
```bash
# Find php.ini
php --ini

# Edit php.ini and uncomment:
extension=mysqli
```

#### "Admin user not found"
```bash
# Import database
mysql -u root -p user_db < Database/127_0_0_1.sql
```

### Verification Commands

```bash
# Check PHP version and mysqli
php -r "echo 'PHP: ' . PHP_VERSION . PHP_EOL; echo 'mysqli: ' . (extension_loaded('mysqli') ? 'OK' : 'MISSING') . PHP_EOL;"

# Check database connection
mysql -u root -p user_db -e "SELECT username FROM users WHERE username='admin';"

# Check database structure
mysql -u root -p user_db -e "DESCRIBE users;"
```

## Test Output Examples

### Bug Condition Tests (Unfixed Code)

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                    BUG CONDITION EXPLORATION TESTS                             ║
║                                                                                ║
║  CRITICAL: These tests MUST FAIL on unfixed code                              ║
║  Failure confirms the vulnerabilities exist                                   ║
╚════════════════════════════════════════════════════════════════════════════════╝

✓ Database connection established successfully

================================================================================
Test 1: SQL Injection - Login Bypass (connection.php)
================================================================================
✗ FAILED: SQL injection bypassed authentication (2 rows returned, expected 0)

[... more failures ...]

╔════════════════════════════════════════════════════════════════════════════════╗
║                           COUNTEREXAMPLES FOUND                                ║
║                                                                                ║
║  These failures CONFIRM the vulnerabilities exist in the unfixed code.        ║
║  This is the EXPECTED outcome for bug condition exploration tests.            ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

### Preservation Tests (Unfixed Code)

```
╔════════════════════════════════════════════════════════════════════════════════╗
║                    PRESERVATION PROPERTY TESTS                                 ║
║                                                                                ║
║  IMPORTANT: These tests MUST PASS on unfixed code                             ║
║  They capture legitimate user operations that must be preserved               ║
╚════════════════════════════════════════════════════════════════════════════════╝

✓ Database connection established successfully

================================================================================
Test 1: Authentication Success with Valid Credentials
================================================================================
✓ PASSED: Authentication with valid credentials

[... more passes ...]

╔════════════════════════════════════════════════════════════════════════════════╗
║                          ALL TESTS PASSED!                                     ║
║                                                                                ║
║  SUCCESS: Baseline behavior captured successfully.                            ║
║  These tests establish the preservation requirements for security fixes.      ║
╚════════════════════════════════════════════════════════════════════════════════╝
```

## Documentation Files

- **`tests/README.md`** - Bug condition tests documentation
- **`tests/PRESERVATION_README.md`** - Preservation tests documentation
- **`tests/TASK1_COMPLETION.md`** - Task 1 completion summary
- **`tests/TASK2_COMPLETION.md`** - Task 2 completion summary
- **`tests/COUNTEREXAMPLES.md`** - Documented counterexamples from Task 1
- **`tests/SETUP.md`** - Detailed setup instructions
- **`TESTING_QUICKSTART.md`** - Quick start guide
- **`tests/RUNNING_ALL_TESTS.md`** - This file

## Important Notes

⚠️ **Run tests on local development environment only**  
⚠️ **Never run on production systems**  
⚠️ **Bug condition tests SHOULD FAIL on unfixed code**  
⚠️ **Preservation tests SHOULD PASS on unfixed code**  
⚠️ **Both test suites SHOULD PASS on fixed code**  

## Success Criteria

### Task 1 Complete
- ✓ Bug condition tests written
- ✓ Tests run on unfixed code
- ✓ Tests FAIL as expected (vulnerabilities confirmed)
- ✓ Counterexamples documented

### Task 2 Complete
- ✓ Preservation tests written
- ✓ Tests run on unfixed code
- ✓ Tests PASS as expected (baseline captured)
- ✓ Baseline behavior documented

### Task 3 Complete
- ✓ Security fixes implemented
- ✓ Bug condition tests re-run and PASS (vulnerabilities fixed)
- ✓ Preservation tests re-run and PASS (no regressions)
- ✓ All requirements validated

---

**Complete Testing Guide** - Both test suites ready to validate security fixes!


````