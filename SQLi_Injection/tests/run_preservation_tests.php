<?php
/**
 * Standalone Preservation Property Test Runner
 * 
 * This script runs preservation property tests WITHOUT requiring PHPUnit installation.
 * These tests MUST PASS on unfixed code to establish baseline behavior.
 * 
 * Usage: php tests/run_preservation_tests.php
 */

// Database configuration
$db_host = "localhost";
$db_user = "root";
$db_pass = "";
$db_name = "user_db";

// Test results tracking
$tests_run = 0;
$tests_passed = 0;
$tests_failed = 0;
$failures = [];

// ANSI color codes for terminal output
$COLOR_GREEN = "\033[32m";
$COLOR_RED = "\033[31m";
$COLOR_YELLOW = "\033[33m";
$COLOR_BLUE = "\033[34m";
$COLOR_RESET = "\033[0m";
$COLOR_BOLD = "\033[1m";

// Check if running in Windows CMD (no color support)
$is_windows = strtoupper(substr(PHP_OS, 0, 3)) === 'WIN';
if ($is_windows) {
    $COLOR_GREEN = $COLOR_RED = $COLOR_YELLOW = $COLOR_BLUE = $COLOR_RESET = $COLOR_BOLD = "";
}

/**
 * Print a formatted header
 */
function printHeader($title) {
    global $COLOR_BOLD, $COLOR_BLUE, $COLOR_RESET;
    echo "\n";
    echo str_repeat("=", 80) . "\n";
    echo $COLOR_BOLD . $COLOR_BLUE . $title . $COLOR_RESET . "\n";
    echo str_repeat("=", 80) . "\n";
}

/**
 * Print a test result
 */
function printResult($test_name, $passed, $message = "") {
    global $COLOR_GREEN, $COLOR_RED, $COLOR_RESET;
    $status = $passed ? $COLOR_GREEN . "✓ PASSED" . $COLOR_RESET : $COLOR_RED . "✗ FAILED" . $COLOR_RESET;
    echo "$status: $test_name\n";
    if (!$passed && $message) {
        echo "  Reason: $message\n";
    }
}

/**
 * Assert helper functions
 */
function assertTrue($condition, $message) {
    if (!$condition) {
        throw new Exception($message);
    }
}

function assertFalse($condition, $message) {
    if ($condition) {
        throw new Exception($message);
    }
}

function assertEquals($expected, $actual, $message) {
    if ($expected != $actual) {
        throw new Exception("$message (Expected: $expected, Actual: $actual)");
    }
}

function assertNotEquals($expected, $actual, $message) {
    if ($expected == $actual) {
        throw new Exception("$message (Expected NOT: $expected, Actual: $actual)");
    }
}

function assertGreaterThan($threshold, $actual, $message) {
    if ($actual <= $threshold) {
        throw new Exception("$message (Expected > $threshold, Actual: $actual)");
    }
}

function assertNotFalse($value, $message) {
    if ($value === false) {
        throw new Exception($message);
    }
}

function assertArrayHasKey($key, $array, $message) {
    if (!array_key_exists($key, $array)) {
        throw new Exception("$message (Key '$key' not found in array)");
    }
}

// Print banner
echo "\n";
echo $COLOR_BOLD . "╔════════════════════════════════════════════════════════════════════════════════╗\n";
echo "║                    PRESERVATION PROPERTY TESTS                                 ║\n";
echo "║                                                                                ║\n";
echo "║  IMPORTANT: These tests MUST PASS on unfixed code                             ║\n";
echo "║  They capture legitimate user operations that must be preserved               ║\n";
echo "╚════════════════════════════════════════════════════════════════════════════════╝" . $COLOR_RESET . "\n";

// Establish database connection
$conn = mysqli_connect($db_host, $db_user, $db_pass, $db_name);
if (!$conn) {
    echo $COLOR_RED . "\n✗ FATAL ERROR: Database connection failed: " . mysqli_connect_error() . $COLOR_RESET . "\n";
    echo "Please ensure:\n";
    echo "  1. MySQL/MariaDB is running\n";
    echo "  2. Database 'user_db' exists\n";
    echo "  3. Connection credentials are correct (localhost, root, no password)\n";
    exit(1);
}

echo $COLOR_GREEN . "\n✓ Database connection established successfully\n" . $COLOR_RESET;

// Test 1: Authentication Success with Valid Credentials
printHeader("Test 1: Authentication Success with Valid Credentials");
echo "Validates: Requirements 3.1, 3.8\n";
echo "Testing: Login with valid credentials (admin/admin123) should authenticate\n\n";
$tests_run++;
try {
    $valid_username = "admin";
    $valid_password = "admin123";
    
    $sql = "SELECT * FROM `users` WHERE `username` = '$valid_username' AND `password` = '$valid_password'";
    $result = mysqli_query($conn, $sql);
    $num_rows = mysqli_num_rows($result);
    
    assertGreaterThan(0, $num_rows, "Valid credentials (admin/admin123) should authenticate successfully. Found $num_rows rows, expected > 0.");
    
    $user_data = mysqli_fetch_assoc($result);
    assertEquals($valid_username, $user_data['username'], "Authenticated user should have username 'admin'");
    
    printResult("Authentication with valid credentials", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("Authentication with valid credentials", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 1: " . $e->getMessage();
}

// Test 2: Authentication Failure with Invalid Credentials
printHeader("Test 2: Authentication Failure with Invalid Credentials");
echo "Validates: Requirements 3.2\n";
echo "Testing: Login with invalid credentials should fail authentication\n\n";
$tests_run++;
try {
    $invalid_username = "nonexistent_user";
    $invalid_password = "wrong_password";
    
    $sql = "SELECT * FROM `users` WHERE `username` = '$invalid_username' AND `password` = '$invalid_password'";
    $result = mysqli_query($conn, $sql);
    $num_rows = mysqli_num_rows($result);
    
    assertEquals(0, $num_rows, "Invalid credentials should NOT authenticate. Found $num_rows rows, expected 0.");
    
    printResult("Authentication failure with invalid credentials", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("Authentication failure with invalid credentials", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 2: " . $e->getMessage();
}

// Test 3: User Creation with Valid Data
printHeader("Test 3: User Creation with Valid Data");
echo "Validates: Requirements 3.3\n";
echo "Testing: Create user with valid data should insert record\n\n";
$tests_run++;
try {
    $test_username = "preservation_test_user_" . time();
    $test_email = "preservation@example.com";
    $test_password = "TestPassword123";
    $test_gender = "Male";
    
    $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')";
    $result = mysqli_query($conn, $sql);
    
    assertTrue($result, "User creation with valid data should succeed");
    
    $test_id = mysqli_insert_id($conn);
    assertGreaterThan(0, $test_id, "Inserted user should have a valid ID");
    
    $check_sql = "SELECT * FROM `users` WHERE id='$test_id'";
    $check_result = mysqli_query($conn, $check_sql);
    $user_data = mysqli_fetch_assoc($check_result);
    
    assertEquals($test_username, $user_data['username'], "Username should match");
    assertEquals($test_email, $user_data['email'], "Email should match");
    assertEquals($test_password, $user_data['password'], "Password should match");
    assertEquals($test_gender, $user_data['gender'], "Gender should match");
    
    mysqli_query($conn, "DELETE FROM `users` WHERE id='$test_id'");
    
    printResult("User creation with valid data", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("User creation with valid data", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 3: " . $e->getMessage();
}

// Test 4: User Update with Valid Data
printHeader("Test 4: User Update with Valid Data");
echo "Validates: Requirements 3.4\n";
echo "Testing: Update user with valid data should modify record\n\n";
$tests_run++;
try {
    $original_username = "update_test_user_" . time();
    $original_email = "update@example.com";
    $original_password = "OriginalPass123";
    $original_gender = "Female";
    
    mysqli_query($conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$original_username','$original_email','$original_password','$original_gender')");
    $test_id = mysqli_insert_id($conn);
    
    $updated_username = "updated_user_" . time();
    $updated_email = "updated@example.com";
    $updated_password = "UpdatedPass123";
    $updated_gender = "Male";
    
    $sql = "UPDATE `users` SET `username`='$updated_username',`email`='$updated_email',`password`='$updated_password',`gender`='$updated_gender' WHERE id='$test_id'";
    $result = mysqli_query($conn, $sql);
    
    assertTrue($result, "User update with valid data should succeed");
    
    $check_sql = "SELECT * FROM `users` WHERE id='$test_id'";
    $check_result = mysqli_query($conn, $check_sql);
    $user_data = mysqli_fetch_assoc($check_result);
    
    assertEquals($updated_username, $user_data['username'], "Username should be updated");
    assertEquals($updated_email, $user_data['email'], "Email should be updated");
    assertEquals($updated_password, $user_data['password'], "Password should be updated");
    assertEquals($updated_gender, $user_data['gender'], "Gender should be updated");
    
    mysqli_query($conn, "DELETE FROM `users` WHERE id='$test_id'");
    
    printResult("User update with valid data", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("User update with valid data", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 4: " . $e->getMessage();
}

// Test 5: User Deletion with Valid ID
printHeader("Test 5: User Deletion with Valid ID");
echo "Validates: Requirements 3.5\n";
echo "Testing: Delete user with valid ID should remove record\n\n";
$tests_run++;
try {
    $test_username = "delete_test_user_" . time();
    $test_email = "delete@example.com";
    $test_password = "DeletePass123";
    $test_gender = "Male";
    
    mysqli_query($conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')");
    $test_id = mysqli_insert_id($conn);
    
    $check_before = mysqli_query($conn, "SELECT * FROM `users` WHERE id='$test_id'");
    assertEquals(1, mysqli_num_rows($check_before), "User should exist before deletion");
    
    $sql = "delete from `users` where id=$test_id";
    $result = mysqli_query($conn, $sql);
    
    assertTrue($result, "User deletion with valid ID should succeed");
    
    $check_after = mysqli_query($conn, "SELECT * FROM `users` WHERE id='$test_id'");
    assertEquals(0, mysqli_num_rows($check_after), "User should be deleted");
    
    printResult("User deletion with valid ID", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("User deletion with valid ID", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 5: " . $e->getMessage();
}

// Test 6: User Display Shows Correct Data
printHeader("Test 6: User Display Shows Correct Data");
echo "Validates: Requirements 3.6\n";
echo "Testing: show_users.php query should return user data correctly\n\n";
$tests_run++;
try {
    $test_username = "display_test_user_" . time();
    $test_email = "display@example.com";
    $test_password = "DisplayPass123";
    $test_gender = "Female";
    
    mysqli_query($conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')");
    $test_id = mysqli_insert_id($conn);
    
    $sql = "SELECT * FROM `users`";
    $result = mysqli_query($conn, $sql);
    
    assertNotFalse($result, "User display query should succeed");
    assertGreaterThan(0, mysqli_num_rows($result), "User display should return at least one user");
    
    $found = false;
    while ($row = mysqli_fetch_assoc($result)) {
        if ($row['id'] == $test_id) {
            $found = true;
            assertEquals($test_username, $row['username'], "Username should be displayed");
            assertEquals($test_email, $row['email'], "Email should be displayed");
            assertEquals($test_gender, $row['gender'], "Gender should be displayed");
            assertArrayHasKey('password', $row, "Password column exists in current implementation");
        }
    }
    
    assertTrue($found, "Test user should be found in display results");
    
    mysqli_query($conn, "DELETE FROM `users` WHERE id='$test_id'");
    
    printResult("User display shows correct data", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("User display shows correct data", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 6: " . $e->getMessage();
}

// Test 7: Database Connection with Existing Parameters
printHeader("Test 7: Database Connection with Existing Parameters");
echo "Validates: Requirements 3.7\n";
echo "Testing: Database connection with existing parameters should succeed\n\n";
$tests_run++;
try {
    $test_conn = mysqli_connect($db_host, $db_user, $db_pass, $db_name);
    
    assertNotFalse($test_conn, "Database connection with existing parameters should succeed");
    assertFalse(mysqli_connect_errno(), "Connection should not have errors");
    
    $test_query = mysqli_query($test_conn, "SELECT 1");
    assertNotFalse($test_query, "Should be able to execute queries on the connection");
    
    mysqli_close($test_conn);
    
    printResult("Database connection with existing parameters", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("Database connection with existing parameters", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 7: " . $e->getMessage();
}

// Test 8: Existing Test Users Authenticate Successfully
printHeader("Test 8: Existing Test Users Authenticate Successfully");
echo "Validates: Requirements 3.8\n";
echo "Testing: Existing test users (admin/admin123) should authenticate\n\n";
$tests_run++;
try {
    $admin_username = "admin";
    $admin_password = "admin123";
    
    $sql = "SELECT * FROM `users` WHERE `username` = '$admin_username' AND `password` = '$admin_password'";
    $result = mysqli_query($conn, $sql);
    
    assertGreaterThan(0, mysqli_num_rows($result), "Admin user (admin/admin123) should authenticate successfully");
    
    $shashank_username = "shashank";
    $shashank_password = "shashank123";
    
    $sql2 = "SELECT * FROM `users` WHERE `username` = '$shashank_username' AND `password` = '$shashank_password'";
    $result2 = mysqli_query($conn, $sql2);
    
    assertNotFalse($result2, "Query for shashank user should execute successfully");
    
    printResult("Existing test users authenticate successfully", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("Existing test users authenticate successfully", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 8: " . $e->getMessage();
}

// Test 9: Multiple Valid Operations in Sequence
printHeader("Test 9: Multiple Valid Operations in Sequence (Full Lifecycle)");
echo "Validates: Requirements 3.3, 3.4, 3.5, 3.6\n";
echo "Testing: Create → Update → Display → Delete sequence should work\n\n";
$tests_run++;
try {
    $username = "lifecycle_test_" . time();
    $email = "lifecycle@example.com";
    $password = "LifecyclePass123";
    $gender = "Female";
    
    $create_sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$username','$email','$password','$gender')";
    $create_result = mysqli_query($conn, $create_sql);
    assertTrue($create_result, "Step 1: User creation should succeed");
    
    $user_id = mysqli_insert_id($conn);
    
    $new_username = "updated_lifecycle_" . time();
    $update_sql = "UPDATE `users` SET `username`='$new_username' WHERE id='$user_id'";
    $update_result = mysqli_query($conn, $update_sql);
    assertTrue($update_result, "Step 2: User update should succeed");
    
    $display_sql = "SELECT * FROM `users` WHERE id='$user_id'";
    $display_result = mysqli_query($conn, $display_sql);
    $user_data = mysqli_fetch_assoc($display_result);
    assertEquals($new_username, $user_data['username'], "Step 3: Updated username should be displayed");
    
    $delete_sql = "delete from `users` where id=$user_id";
    $delete_result = mysqli_query($conn, $delete_sql);
    assertTrue($delete_result, "Step 4: User deletion should succeed");
    
    $verify_sql = "SELECT * FROM `users` WHERE id='$user_id'";
    $verify_result = mysqli_query($conn, $verify_sql);
    assertEquals(0, mysqli_num_rows($verify_result), "Step 5: User should be deleted");
    
    printResult("Multiple valid operations in sequence", true);
    $tests_passed++;
} catch (Exception $e) {
    printResult("Multiple valid operations in sequence", false, $e->getMessage());
    $tests_failed++;
    $failures[] = "Test 9: " . $e->getMessage();
}

// Close database connection
mysqli_close($conn);

// Print summary
echo "\n";
echo $COLOR_BOLD . "╔════════════════════════════════════════════════════════════════════════════════╗\n";
echo "║                              TEST SUMMARY                                      ║\n";
echo "╚════════════════════════════════════════════════════════════════════════════════╝" . $COLOR_RESET . "\n";
echo "\n";
echo "Total Tests Run: $tests_run\n";
echo $COLOR_GREEN . "Tests Passed: $tests_passed" . $COLOR_RESET . "\n";
echo $COLOR_RED . "Tests Failed: $tests_failed" . $COLOR_RESET . "\n";
echo "\n";

if ($tests_failed > 0) {
    echo $COLOR_BOLD . $COLOR_RED . "╔════════════════════════════════════════════════════════════════════════════════╗\n";
    echo "║                              FAILURES DETECTED                                 ║\n";
    echo "║                                                                                ║\n";
    echo "║  WARNING: Preservation tests should PASS on unfixed code!                     ║\n";
    echo "║  These failures indicate the baseline behavior is not as expected.            ║\n";
    echo "╚════════════════════════════════════════════════════════════════════════════════╝" . $COLOR_RESET . "\n";
    echo "\n";
    echo "Failed Tests:\n";
    foreach ($failures as $failure) {
        echo $COLOR_RED . "  • $failure" . $COLOR_RESET . "\n";
    }
    echo "\n";
    exit(1);
} else {
    echo $COLOR_BOLD . $COLOR_GREEN . "╔════════════════════════════════════════════════════════════════════════════════╗\n";
    echo "║                          ALL TESTS PASSED!                                     ║\n";
    echo "║                                                                                ║\n";
    echo "║  SUCCESS: Baseline behavior captured successfully.                            ║\n";
    echo "║  These tests establish the preservation requirements for security fixes.      ║\n";
    echo "╚════════════════════════════════════════════════════════════════════════════════╝" . $COLOR_RESET . "\n";
    echo "\n";
    exit(0);
}
