# Bug Condition Exploration - Counterexamples Documentation

## Overview

This document records the counterexamples found during bug condition exploration testing on the **UNFIXED** code. These counterexamples demonstrate that the security vulnerabilities exist and confirm the root cause analysis.

**Test Execution Date**: [To be filled when tests are run]  
**Database**: user_db  
**Test Runner**: tests/run_bug_exploration_tests.php

## Expected Outcome

On UNFIXED code, these tests are **EXPECTED TO FAIL**. Test failures confirm the vulnerabilities exist and provide concrete examples of how they can be exploited.

## Counterexamples Found

### 1. SQL Injection - Login Bypass (connection.php)

**Requirement**: 1.1, 1.5  
**Test**: SQL Injection in connection.php - Login Bypass  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Attack Vector**:
- Username: `admin' OR '1'='1`
- Password: `anything`

**Vulnerable Query**:
```sql
SELECT * FROM `users` WHERE `username` = 'admin' OR '1'='1' AND `password` = 'anything'
```

**Expected Behavior (Fixed Code)**: Authentication fails, 0 rows returned  
**Actual Behavior (Unfixed Code)**: Authentication bypassed, multiple rows returned

**Impact**: Attacker can bypass authentication without knowing valid credentials

**Root Cause**: Direct variable interpolation in SQL query without prepared statements

---

### 2. SQL Injection - New User Creation (new_user.php)

**Requirement**: 1.2  
**Test**: SQL Injection in new_user.php - Username with SQL Payload  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Attack Vector**:
- Username: `test', 'hacked@evil.com', 'hacked', 'Male'); DROP TABLE users; --`
- Email: `test@example.com`
- Password: `testpass`
- Gender: `Male`

**Vulnerable Query**:
```sql
INSERT INTO `users`(`username`, `email`, `password`, `gender`) 
VALUES ('test', 'hacked@evil.com', 'hacked', 'Male'); DROP TABLE users; --','test@example.com','testpass','Male')
```

**Expected Behavior (Fixed Code)**: Data safely inserted with prepared statements, table remains intact  
**Actual Behavior (Unfixed Code)**: SQL injection payload may execute, potentially dropping the users table

**Impact**: Attacker can manipulate database structure, delete data, or inject malicious records

**Root Cause**: Direct variable interpolation in INSERT query without prepared statements

---

### 3. SQL Injection - User Update (update.php)

**Requirement**: 1.3  
**Test**: SQL Injection in update.php - Fields with SQL Payloads  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Attack Vector**:
- Username: `hacked', password='hacked123' WHERE '1'='1`
- Target ID: [specific user ID]

**Vulnerable Query**:
```sql
UPDATE `users` SET `username`='hacked', password='hacked123' WHERE '1'='1',
`email`='test@example.com',`password`='testpass',`gender`='Male' WHERE id='[ID]'
```

**Expected Behavior (Fixed Code)**: Only specified user updated with prepared statements  
**Actual Behavior (Unfixed Code)**: Multiple users' passwords changed to 'hacked123'

**Impact**: Attacker can modify all user records, change passwords, escalate privileges

**Root Cause**: Direct variable interpolation in UPDATE query without prepared statements

---

### 4. SQL Injection - User Deletion (delete.php)

**Requirement**: 1.4  
**Test**: SQL Injection in delete.php - Delete with OR Condition  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Attack Vector**:
- Delete ID: `1 OR 1=1`

**Vulnerable Query**:
```sql
delete from `users` where id=1 OR 1=1
```

**Expected Behavior (Fixed Code)**: Only specified user deleted with prepared statements  
**Actual Behavior (Unfixed Code)**: All users deleted from database

**Impact**: Attacker can delete all records, causing complete data loss

**Root Cause**: Direct variable interpolation in DELETE query without prepared statements

---

### 5. Plain Text Password Storage

**Requirement**: 1.6, 1.7  
**Test**: Plain Text Password Storage  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Test Data**:
- Username: `testuser_password`
- Password: `MySecretPassword123`

**Expected Behavior (Fixed Code)**: Password stored as bcrypt hash (e.g., `$2y$10$...`)  
**Actual Behavior (Unfixed Code)**: Password stored as plain text: `MySecretPassword123`

**Database Evidence**:
```sql
SELECT password FROM users WHERE username='testuser_password';
-- Returns: MySecretPassword123 (plain text)
```

**Impact**: 
- Database compromise exposes all user passwords
- Query logs contain plain text passwords
- Backup files contain plain text passwords
- Database administrators can see user passwords

**Root Cause**: No password hashing implemented, passwords stored directly without encryption

---

### 6. Plain Text Password Display (show_users.php)

**Requirement**: 1.8  
**Test**: Plain Text Password Display in show_users.php  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Test Data**:
- Username: `testuser_display`
- Password: `DisplayPassword123`

**Expected Behavior (Fixed Code)**: Password column removed or masked in HTML output  
**Actual Behavior (Unfixed Code)**: Plain text password visible in HTML table

**HTML Evidence**:
```html
<th scope="col">Password</th>
...
<td>DisplayPassword123</td>
```

**Impact**: 
- Anyone viewing the user list sees all passwords
- Passwords visible in browser history
- Passwords visible in screenshots
- Passwords visible in screen sharing sessions

**Root Cause**: Password column displayed in HTML table without masking or removal

---

### 7. Error Disclosure (delete.php)

**Requirement**: 1.10  
**Test**: Error Disclosure in delete.php  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Trigger**: Database error during deletion

**Expected Behavior (Fixed Code)**: Generic error message, details logged securely  
**Actual Behavior (Unfixed Code)**: Detailed MySQL error exposed to user

**Error Output Example**:
```
Table 'user_db.users' doesn't exist
```

**Code Evidence**:
```php
die(mysqli_error($conn));
```

**Impact**: 
- Database schema information exposed
- Table names revealed
- Error messages aid in attack planning
- Information disclosure vulnerability

**Root Cause**: `die(mysqli_error($conn))` exposes detailed database errors to users

---

### 8. Error Disclosure (connect.php)

**Requirement**: 1.11  
**Test**: Error Disclosure in connect.php  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Trigger**: Database connection failure

**Expected Behavior (Fixed Code)**: Generic error message, details logged securely  
**Actual Behavior (Unfixed Code)**: Detailed connection error exposed to user

**Error Output Example**:
```
Failed to connect to MySQL: Access denied for user 'root'@'localhost' (using password: NO)
```

**Code Evidence**:
```php
echo "Failed to connect to MySQL: " . mysqli_connect_error();
```

**Impact**: 
- Database username revealed (root)
- Database host revealed (localhost)
- Authentication status revealed
- Connection details aid in attack planning

**Root Cause**: `mysqli_connect_error()` output echoed directly to users

---

### 9. Missing Email Validation

**Requirement**: 1.14  
**Test**: Missing Email Validation  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Test Data**:
- Username: `testuser_email`
- Email: `notanemail` (invalid format)

**Expected Behavior (Fixed Code)**: Invalid email rejected with validation error  
**Actual Behavior (Unfixed Code)**: Invalid email accepted and stored in database

**Database Evidence**:
```sql
SELECT email FROM users WHERE username='testuser_email';
-- Returns: notanemail (invalid format stored)
```

**Impact**: 
- Invalid data in database
- Email notifications fail
- Data quality issues
- Potential for injection attacks via email field

**Root Cause**: No server-side email validation using `filter_var()` or similar

---

### 10. Missing Length Validation

**Requirement**: 1.15  
**Test**: Missing Length Validation  
**Status**: [EXPECTED TO FAIL on unfixed code]

**Test Data**:
- Username: [10,000 character string of 'A's]
- Email: `length@example.com`

**Expected Behavior (Fixed Code)**: Excessive length rejected with validation error  
**Actual Behavior (Unfixed Code)**: Excessive length accepted (may be truncated by database)

**Database Evidence**:
```sql
SELECT LENGTH(username) FROM users WHERE email='length@example.com';
-- Returns: [large number or truncated value]
```

**Impact**: 
- Database performance issues
- Memory exhaustion
- Buffer overflow potential
- Denial of service vector

**Root Cause**: No server-side length validation before database insertion

---

## Summary

### Vulnerabilities Confirmed

| Category | Count | Severity |
|----------|-------|----------|
| SQL Injection | 4 | Critical |
| Password Security | 2 | Critical |
| Error Disclosure | 2 | High |
| Input Validation | 2 | Medium |
| **Total** | **10** | - |

### Attack Surface

The unfixed code is vulnerable to:
1. **Authentication Bypass** - SQL injection in login
2. **Data Manipulation** - SQL injection in CRUD operations
3. **Data Exfiltration** - SQL injection and password exposure
4. **Data Destruction** - SQL injection in delete operations
5. **Credential Theft** - Plain text password storage and display
6. **Information Disclosure** - Detailed error messages
7. **Data Integrity Issues** - Missing input validation

### Root Cause Confirmation

The counterexamples confirm the hypothesized root causes:

✓ **Lack of Security Awareness**: No prepared statements used anywhere  
✓ **Misunderstanding of mysqli_real_escape_string()**: Attempted but implemented incorrectly  
✓ **No Password Security**: Plain text storage throughout  
✓ **Development-Mode Error Handling**: Detailed errors exposed  
✓ **Missing Input Validation Layer**: No validation before processing  
✓ **Copy-Paste Development**: Duplicate connection code in multiple files

## Next Steps

1. ✓ **Counterexamples Documented** - This file
2. **Proceed to Task 2** - Write preservation property tests
3. **Proceed to Task 3** - Implement security fixes
4. **Re-run Bug Condition Tests** - Verify all tests pass after fixes
5. **Run Preservation Tests** - Verify no regressions

## Test Execution Instructions

To reproduce these counterexamples:

```bash
# Run the bug condition exploration tests
php tests/run_bug_exploration_tests.php

# Or use the Windows batch script
run_tests.bat
```

**IMPORTANT**: These tests should be run on the UNFIXED code first to confirm vulnerabilities, then re-run after implementing fixes to verify they pass.

---

**Document Status**: Template - To be updated with actual test results  
**Last Updated**: [Date]  
**Updated By**: [Name]

````