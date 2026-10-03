# SQL Injection Prevention Project - Flow Diagram

## Application Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION FLOW                            │
└─────────────────────────────────────────────────────────────────────────┘

    ┌──────────────┐
    │ index.html   │  Login Page
    │ (Login Form) │
    └──────┬───────┘
           │
           │ POST username & password
           ▼
    ┌──────────────────┐
    │ connection.php   │  ✅ SECURE Authentication
    │                  │  • Prepared statements
    │                  │  • password_verify()
    │                  │  • Input validation
    └──────┬───────────┘
           │
           ├─── Success ──────────────────┐
           │                              │
           ▼                              ▼
    ┌──────────────┐              ┌──────────────┐
    │ admin_page   │              │ index.html   │
    │ .html        │              │ (Error msg)  │
    │ Dashboard    │              └──────────────┘
    └──────┬───────┘
           │
           │ User chooses action
           │
    ┌──────┴──────────────────────────────────────┐
    │                                              │
    ▼                                              ▼
┌─────────────┐                            ┌─────────────┐
│ View Users  │                            │  Add User   │
│             │                            │             │
│ show_users  │                            │ new_users   │
│ .php        │                            │ .html       │
└─────┬───────┘                            └─────┬───────┘
      │                                          │
      │ Display all users                        │ POST form data
      │ (no passwords!)                          ▼
      │                                    ┌─────────────┐
      │                                    │ new_user    │
      │                                    │ .php        │
      │                                    │ ✅ SECURE   │
      │                                    │ • Prepared  │
      │                                    │ • Hash pwd  │
      │                                    │ • Validate  │
      │                                    └─────────────┘
      │
      ├─── Update ────────────────┐
      │                            │
      ▼                            ▼
┌─────────────┐            ┌─────────────┐
│ update.php  │            │ delete.php  │
│ ✅ SECURE   │            │ ✅ SECURE   │
│ • Prepared  │            │ • Prepared  │
│ • Hash pwd  │            │ • Validate  │
│ • Validate  │            │ • ID check  │
└─────────────┘            └─────────────┘
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SECURITY LAYERS                                  │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 1: INPUT VALIDATION                                                │
│ ✓ Email format validation                                                │
│ ✓ Length restrictions (max 200 chars)                                    │
│ ✓ Gender value validation                                                │
│ ✓ ID parameter validation (numeric, positive)                            │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 2: SQL INJECTION PREVENTION                                        │
│ ✓ Prepared statements with parameter binding                             │
│ ✓ No direct SQL concatenation                                            │
│ ✓ mysqli_stmt_bind_param() for all queries                               │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 3: PASSWORD SECURITY                                               │
│ ✓ Bcrypt hashing (password_hash)                                         │
│ ✓ Secure verification (password_verify)                                  │
│ ✓ No plain text storage                                                  │
│ ✓ No password display in UI                                              │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 4: ERROR HANDLING                                                  │
│ ✓ Secure error logging (error_log)                                       │
│ ✓ Generic user messages                                                  │
│ ✓ No database schema exposure                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│ Layer 5: OUTPUT ENCODING                                                 │
│ ✓ htmlspecialchars() for XSS prevention                                  │
│ ✓ Proper character encoding (utf8mb4)                                    │
└─────────────────────────────────────────────────────────────────────────┘
```

## Database Schema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         DATABASE: user_db                                │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│ TABLE: users                                                             │
├─────────────┬──────────────┬──────────────────────────────────────────┤
│ Column      │ Type         │ Description                              │
├─────────────┼──────────────┼──────────────────────────────────────────┤
│ id          │ INT(200)     │ Primary Key, Auto Increment              │
│ username    │ VARCHAR(200) │ User's username                          │
│ email       │ VARCHAR(200) │ User's email (validated)                 │
│ password    │ VARCHAR(200) │ Bcrypt hashed password                   │
│ gender      │ VARCHAR(200) │ Male or Female                           │
└─────────────┴──────────────┴──────────────────────────────────────────┘

Default Users (after migration):
┌────┬──────────┬─────────────────────────────┬──────────────┬────────┐
│ id │ username │ email                       │ password     │ gender │
├────┼──────────┼─────────────────────────────┼──────────────┼────────┤
│ 1  │ admin    │ admin123@gmail.com          │ [bcrypt hash]│ Male   │
│ 2  │ shashank │ shashankghodke3242@gmail.com│ [bcrypt hash]│ Male   │
└────┴──────────┴─────────────────────────────┴──────────────┴────────┘
```

## Testing Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         TESTING WORKFLOW                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 1: Bug Condition Exploration Tests                                 │
│ (tests/BugConditionExplorationTest.php)                                  │
├──────────────────────────────────────────────────────────────────────────┤
│ ✓ Test SQL injection attempts are BLOCKED                                │
│ ✓ Test passwords are HASHED in database                                  │
│ ✓ Test passwords are NOT displayed in UI                                 │
│ ✓ Test error messages are GENERIC                                        │
│ ✓ Test input validation REJECTS invalid data                             │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ PHASE 2: Preservation Property Tests                                     │
│ (tests/PreservationPropertyTest.php)                                     │
├──────────────────────────────────────────────────────────────────────────┤
│ ✓ Test valid login SUCCEEDS                                              │
│ ✓ Test invalid login FAILS appropriately                                 │
│ ✓ Test user creation WORKS                                               │
│ ✓ Test user update WORKS                                                 │
│ ✓ Test user deletion WORKS                                               │
│ ✓ Test user display WORKS (without passwords)                            │
└──────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────┐
│ RESULT: All Tests Pass = Application is SECURE and FUNCTIONAL            │
└──────────────────────────────────────────────────────────────────────────┘
```

## File Dependencies

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FILE RELATIONSHIPS                               │
└─────────────────────────────────────────────────────────────────────────┘

connect.php (Database Connection)
    │
    ├─── connection.php (Login Authentication)
    │
    ├─── new_user.php (Create User)
    │
    ├─── update.php (Update User)
    │
    ├─── delete.php (Delete User)
    │
    └─── show_users.php (Display Users)

index.html ──────► connection.php ──────► admin_page.html
                                              │
                                              ├─► show_users.php
                                              │
                                              └─► new_users.html ──► new_user.php

update.php ◄──── show_users.php ────► delete.php
```

## Migration Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    PASSWORD MIGRATION FLOW                               │
└─────────────────────────────────────────────────────────────────────────┘

BEFORE Migration:
┌────────────────────────────────────────────────────────────────────────┐
│ Database: users table                                                   │
│ password column: "admin123" (PLAIN TEXT - INSECURE!)                    │
└────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Run: php migrate_passwords.php
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Migration Script:                                                       │
│ 1. Read all users from database                                         │
│ 2. Check if password is already hashed                                  │
│ 3. If plain text: hash with password_hash()                             │
│ 4. Update database with hashed password                                 │
│ 5. Log results                                                          │
└────────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
AFTER Migration:
┌────────────────────────────────────────────────────────────────────────┐
│ Database: users table                                                   │
│ password column: "$2y$10$..." (BCRYPT HASH - SECURE!)                   │
└────────────────────────────────────────────────────────────────────────┘

Login Process (After Migration):
┌────────────────────────────────────────────────────────────────────────┐
│ User enters: "admin123"                                                 │
│      ↓                                                                  │
│ connection.php retrieves hash from database                             │
│      ↓                                                                  │
│ password_verify("admin123", "$2y$10$...") → TRUE                        │
│      ↓                                                                  │
│ Login SUCCESS!                                                          │
└────────────────────────────────────────────────────────────────────────┘
```

## Attack Prevention

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    SQL INJECTION ATTACK PREVENTION                       │
└─────────────────────────────────────────────────────────────────────────┘

VULNERABLE CODE (Before Fix):
┌────────────────────────────────────────────────────────────────────────┐
│ $sql = "SELECT * FROM users WHERE username='$uname' AND password='$pass'";│
│ $result = mysqli_query($conn, $sql);                                    │
└────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Attacker enters:
                                  │ Username: admin' OR '1'='1
                                  │ Password: anything
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Executed Query:                                                         │
│ SELECT * FROM users WHERE username='admin' OR '1'='1' AND password='...'│
│                                                                         │
│ Result: '1'='1' is always TRUE → Authentication BYPASSED! ❌            │
└────────────────────────────────────────────────────────────────────────┘

SECURE CODE (After Fix):
┌────────────────────────────────────────────────────────────────────────┐
│ $stmt = mysqli_prepare($conn, "SELECT * FROM users WHERE username = ?");│
│ mysqli_stmt_bind_param($stmt, "s", $uname);                             │
│ mysqli_stmt_execute($stmt);                                             │
└────────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Attacker enters:
                                  │ Username: admin' OR '1'='1
                                  │ Password: anything
                                  ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Executed Query:                                                         │
│ SELECT * FROM users WHERE username = "admin' OR '1'='1"                 │
│                                                                         │
│ Result: Searches for literal username "admin' OR '1'='1"                │
│         No user found → Authentication FAILS! ✅                         │
└────────────────────────────────────────────────────────────────────────┘
```

## Summary

This project demonstrates a complete security transformation:

**Before:** Vulnerable to SQL injection, plain text passwords, information disclosure
**After:** Secure with prepared statements, bcrypt hashing, proper error handling

All changes are verified through comprehensive property-based testing.

````