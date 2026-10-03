<?php
/**
 * Bug Condition Exploration Test Runner
 * 
 * CRITICAL: These tests MUST FAIL on unfixed code - failure confirms vulnerabilities exist
 * DO NOT attempt to fix the tests or the code when they fail
 * These tests encode the EXPECTED SECURE BEHAVIOR
 * 
 * Run with: php tests/run_bug_exploration_tests.php
 * 
 * **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15**
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
$counterexamples = [];

// Helper function to run a test
function runTest($test_name, $test_function) {
    global $tests_run, $tests_passed, $tests_failed, $counterexamples;
    
    $tests_run++;
    echo "\n" . str_repeat("=", 80) . "\n";
    echo "Running Test $tests_run: $test_name\n";
    echo str_repeat("=", 80) . "\n";
    
    try {
        $result = $test_function();
        if ($result['passed']) {
            $tests_passed++;
            echo "✓ PASSED: {$result['message']}\n";
        } else {
            $tests_failed++;
            echo "✗ FAILED: {$result['message']}\n";
            $counterexamples[] = [
                'test' => $test_name,
                'message' => $result['message'],
                'details' => $result['details'] ?? ''
            ];
        }
    } catch (Exception $e) {
        $tests_failed++;
        echo "✗ ERROR: " . $e->getMessage() . "\n";
        $counterexamples[] = [
            'test' => $test_name,
            'message' => 'Exception: ' . $e->getMessage(),
            'details' => $e->getTraceAsString()
        ];
    }
}

// Establish database connection
$conn = mysqli_connect($db_host, $db_user, $db_pass, $db_name);
if (!$conn) {
    die("Database connection failed: " . mysqli_connect_error() . "\n");
}

echo "\n";
echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
echo "║                    BUG CONDITION EXPLORATION TESTS                             ║\n";
echo "║                                                                                ║\n";
echo "║  CRITICAL: These tests MUST FAIL on unfixed code                              ║\n";
echo "║  Failure confirms the vulnerabilities exist                                   ║\n";
echo "╚════════════════════════════════════════════════════════════════════════════════╝\n";

// Test 1: SQL Injection in connection.php - Login Bypass
runTest("SQL Injection - Login Bypass (connection.php)", function() use ($conn) {
    $malicious_username = "admin' OR '1'='1";
    $malicious_password = "anything";
    
    $sql = "SELECT * FROM `users` WHERE `username` = '$malicious_username' AND `password` = '$malicious_password'";
    $result = mysqli_query($conn, $sql);
    $num_rows = mysqli_num_rows($result);
    
    $passed = ($num_rows === 0);
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "SQL injection correctly blocked (0 rows returned)" 
            : "SQL injection bypassed authentication ($num_rows rows returned, expected 0)",
        'details' => "Query: $sql\nRows returned: $num_rows"
    ];
});

// Test 2: SQL Injection in new_user.php - Username with SQL Payload
runTest("SQL Injection - New User Creation (new_user.php)", function() use ($conn) {
    $malicious_username = "test', 'hacked@evil.com', 'hacked', 'Male'); DROP TABLE users; --";
    $email = "test@example.com";
    $password = "testpass";
    $gender = "Male";
    
    $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$malicious_username','$email','$password','$gender')";
    @mysqli_query($conn, $sql);
    
    $check_table = mysqli_query($conn, "SHOW TABLES LIKE 'users'");
    $table_exists = mysqli_num_rows($check_table) > 0;
    
    // Clean up
    mysqli_query($conn, "DELETE FROM `users` WHERE `username` LIKE '%test%' OR `username` LIKE '%DROP%'");
    
    $passed = $table_exists;
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "SQL injection correctly prevented (users table still exists)" 
            : "SQL injection executed DROP TABLE command (users table deleted)",
        'details' => "Table exists: " . ($table_exists ? "Yes" : "No")
    ];
});

// Test 3: SQL Injection in update.php - Fields with SQL Payloads
runTest("SQL Injection - User Update (update.php)", function() use ($conn) {
    // Create test user
    $test_username = "testuser_update";
    mysqli_query($conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','test@example.com','testpass','Male')");
    $test_id = mysqli_insert_id($conn);
    
    // Attempt SQL injection
    $malicious_username = "hacked', password='hacked123' WHERE '1'='1";
    $sql = "UPDATE `users` SET `username`='$malicious_username',`email`='test@example.com',`password`='testpass',`gender`='Male' WHERE id='$test_id'";
    @mysqli_query($conn, $sql);
    
    // Check if other users were affected
    $affected_users = mysqli_query($conn, "SELECT * FROM `users` WHERE `password` = 'hacked123'");
    $num_affected = mysqli_num_rows($affected_users);
    
    // Clean up
    mysqli_query($conn, "DELETE FROM `users` WHERE id='$test_id' OR `username` LIKE '%hacked%'");
    mysqli_query($conn, "UPDATE `users` SET `password` = 'admin123' WHERE `username` = 'admin' AND `password` = 'hacked123'");
    
    $passed = ($num_affected === 0);
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "SQL injection correctly prevented (0 users affected)" 
            : "SQL injection modified multiple users ($num_affected users affected, expected 0)",
        'details' => "Users with 'hacked123' password: $num_affected"
    ];
});

// Test 4: SQL Injection in delete.php - Delete with OR Condition
runTest("SQL Injection - User Deletion (delete.php)", function() use ($conn) {
    // Create test users
    mysqli_query($conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('testuser1','test1@example.com','pass1','Male')");
    $id1 = mysqli_insert_id($conn);
    mysqli_query($conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('testuser2','test2@example.com','pass2','Female')");
    $id2 = mysqli_insert_id($conn);
    
    $count_before = mysqli_num_rows(mysqli_query($conn, "SELECT * FROM `users`"));
    
    // Attempt SQL injection
    $malicious_id = "$id1 OR 1=1";
    $sql = "delete from `users` where id=$malicious_id";
    @mysqli_query($conn, $sql);
    
    $count_after = mysqli_num_rows(mysqli_query($conn, "SELECT * FROM `users`"));
    
    // Clean up
    mysqli_query($conn, "DELETE FROM `users` WHERE id IN ('$id1', '$id2')");
    
    $passed = ($count_after > 0);
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "SQL injection correctly prevented ($count_after users remain)" 
            : "SQL injection deleted all users (0 users remain, expected > 0)",
        'details' => "Users before: $count_before, Users after: $count_after"
    ];
});

// Test 5: Plain Text Password Storage
runTest("Plain Text Password Storage", function() use ($conn) {
    $test_username = "testuser_password";
    $test_password = "MySecretPassword123";
    
    $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','testpass@example.com','$test_password','Male')";
    mysqli_query($conn, $sql);
    $test_id = mysqli_insert_id($conn);
    
    $result = mysqli_query($conn, "SELECT `password` FROM `users` WHERE id='$test_id'");
    $row = mysqli_fetch_assoc($result);
    $stored_password = $row['password'];
    
    // Clean up
    mysqli_query($conn, "DELETE FROM `users` WHERE id='$test_id'");
    
    $is_hashed = (strpos($stored_password, '$2y$') === 0);
    $is_plain_text = ($stored_password === $test_password);
    
    $passed = $is_hashed && !$is_plain_text;
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "Password correctly hashed (bcrypt format)" 
            : "Password stored in plain text (expected bcrypt hash starting with \$2y\$)",
        'details' => "Stored password: " . substr($stored_password, 0, 30) . "...\nIs bcrypt hash: " . ($is_hashed ? "Yes" : "No") . "\nIs plain text: " . ($is_plain_text ? "Yes" : "No")
    ];
});

// Test 6: Plain Text Password Display in show_users.php
runTest("Plain Text Password Display (show_users.php)", function() use ($conn) {
    // Create test user
    $test_username = "testuser_display";
    $test_password = "DisplayPassword123";
    mysqli_query($conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','display@example.com','$test_password','Female')");
    $test_id = mysqli_insert_id($conn);
    
    // Capture output
    ob_start();
    include __DIR__ . '/../show_users.php';
    $output = ob_get_clean();
    
    // Clean up
    mysqli_query($conn, "DELETE FROM `users` WHERE id='$test_id'");
    
    $password_visible = (strpos($output, $test_password) !== false);
    $password_column_exists = (strpos($output, '<th scope="col">Password</th>') !== false);
    
    $passed = !$password_visible && !$password_column_exists;
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "Password correctly hidden (not visible in output)" 
            : "Password exposed in HTML output (plain text password visible or password column exists)",
        'details' => "Password visible: " . ($password_visible ? "Yes" : "No") . "\nPassword column exists: " . ($password_column_exists ? "Yes" : "No")
    ];
});

// Test 7: Error Disclosure in delete.php
runTest("Error Disclosure (delete.php)", function() use ($conn) {
    // Close connection to force error
    $temp_conn = mysqli_connect("localhost", "root", "", "user_db");
    mysqli_close($temp_conn);
    
    // Create test file that simulates delete.php with error
    $test_code = <<<'PHP'
<?php
$conn = null; // Simulate broken connection
if(isset($_GET['deleteid'])){
    $id=$_GET['deleteid'];
    $sql = "delete from `users` where id=$id";
    $result=@mysqli_query($conn, $sql);
    if($result){
        header('location:show_users.php');
    }else{
        die(mysqli_error($conn));
    }
}
?>
PHP;
    
    file_put_contents(__DIR__ . '/temp_delete_test.php', $test_code);
    
    ob_start();
    $_GET['deleteid'] = 1;
    @include __DIR__ . '/temp_delete_test.php';
    $output = ob_get_clean();
    unset($_GET['deleteid']);
    
    @unlink(__DIR__ . '/temp_delete_test.php');
    
    $error_exposed = (strpos($output, 'mysqli_error') !== false || strpos($output, 'MySQL') !== false);
    
    $passed = !$error_exposed;
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "Errors correctly handled (no MySQL details exposed)" 
            : "Detailed MySQL errors exposed to users",
        'details' => "Error details exposed: " . ($error_exposed ? "Yes" : "No")
    ];
});

// Test 8: Error Disclosure in connect.php
runTest("Error Disclosure (connect.php)", function() {
    $test_connect = <<<'PHP'
<?php
$hostname = "localhost";
$username = "wrong_user";
$password = "wrong_pass";
$dbname = "user_db";
$conn = @mysqli_connect($hostname, $username, $password, $dbname);
if (mysqli_connect_errno()) {
    echo "Failed to connect to MySQL: " . mysqli_connect_error();
}
?>
PHP;
    
    file_put_contents(__DIR__ . '/temp_connect_test.php', $test_connect);
    
    ob_start();
    @include __DIR__ . '/temp_connect_test.php';
    $output = ob_get_clean();
    
    @unlink(__DIR__ . '/temp_connect_test.php');
    
    $error_exposed = (strpos($output, 'mysqli_connect_error') !== false || strpos($output, 'Access denied') !== false);
    
    $passed = !$error_exposed;
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "Connection errors correctly handled (no details exposed)" 
            : "Detailed connection errors exposed to users",
        'details' => "Connection error details exposed: " . ($error_exposed ? "Yes" : "No")
    ];
});

// Test 9: Missing Email Validation
runTest("Missing Email Validation", function() use ($conn) {
    $test_username = "testuser_email";
    $invalid_email = "notanemail";
    
    $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$invalid_email','testpass','Male')";
    $result = @mysqli_query($conn, $sql);
    
    $email_accepted = false;
    if ($result) {
        $test_id = mysqli_insert_id($conn);
        $check = mysqli_query($conn, "SELECT `email` FROM `users` WHERE id='$test_id'");
        $row = mysqli_fetch_assoc($check);
        $stored_email = $row['email'];
        $email_accepted = ($stored_email === $invalid_email);
        
        // Clean up
        mysqli_query($conn, "DELETE FROM `users` WHERE id='$test_id'");
    }
    
    $passed = !$email_accepted;
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "Invalid email correctly rejected" 
            : "Invalid email format '$invalid_email' was accepted and stored",
        'details' => "Invalid email accepted: " . ($email_accepted ? "Yes" : "No")
    ];
});

// Test 10: Missing Length Validation
runTest("Missing Length Validation", function() use ($conn) {
    $excessive_username = str_repeat('A', 10000);
    
    $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$excessive_username','length@example.com','testpass','Male')";
    $result = @mysqli_query($conn, $sql);
    
    $length_accepted = false;
    $stored_length = 0;
    if ($result) {
        $test_id = mysqli_insert_id($conn);
        $check = mysqli_query($conn, "SELECT `username` FROM `users` WHERE id='$test_id'");
        $row = mysqli_fetch_assoc($check);
        $stored_username = $row['username'];
        $stored_length = strlen($stored_username);
        $length_accepted = ($stored_length > 255); // Reasonable max length
        
        // Clean up
        mysqli_query($conn, "DELETE FROM `users` WHERE id='$test_id'");
    }
    
    $passed = !$length_accepted;
    return [
        'passed' => $passed,
        'message' => $passed 
            ? "Excessive length correctly rejected or truncated to reasonable size" 
            : "Excessive length username (10000 chars) was accepted (stored length: $stored_length)",
        'details' => "Stored length: $stored_length characters"
    ];
});

// Close database connection
mysqli_close($conn);

// Print summary
echo "\n";
echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
echo "║                              TEST SUMMARY                                      ║\n";
echo "╚════════════════════════════════════════════════════════════════════════════════╝\n";
echo "\n";
echo "Total Tests Run: $tests_run\n";
echo "Tests Passed: $tests_passed\n";
echo "Tests Failed: $tests_failed\n";
echo "\n";

if ($tests_failed > 0) {
    echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
    echo "║                           COUNTEREXAMPLES FOUND                                ║\n";
    echo "║                                                                                ║\n";
    echo "║  These failures CONFIRM the vulnerabilities exist in the unfixed code.        ║\n";
    echo "║  This is the EXPECTED outcome for bug condition exploration tests.            ║\n";
    echo "╚════════════════════════════════════════════════════════════════════════════════╝\n";
    echo "\n";
    
    foreach ($counterexamples as $i => $example) {
        echo "Counterexample " . ($i + 1) . ": {$example['test']}\n";
        echo "  Message: {$example['message']}\n";
        if (!empty($example['details'])) {
            echo "  Details: {$example['details']}\n";
        }
        echo "\n";
    }
    
    echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
    echo "║                              NEXT STEPS                                        ║\n";
    echo "║                                                                                ║\n";
    echo "║  1. Document these counterexamples                                            ║\n";
    echo "║  2. Proceed to implement security fixes (Task 3)                              ║\n";
    echo "║  3. Re-run these tests after fixes to verify they pass                        ║\n";
    echo "╚════════════════════════════════════════════════════════════════════════════════╝\n";
} else {
    echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
    echo "║                          UNEXPECTED RESULT                                     ║\n";
    echo "║                                                                                ║\n";
    echo "║  All tests passed on unfixed code - this is UNEXPECTED!                       ║\n";
    echo "║  Bug condition exploration tests should FAIL on unfixed code.                 ║\n";
    echo "║  This suggests either:                                                        ║\n";
    echo "║    - The code is already fixed                                                ║\n";
    echo "║    - The tests need adjustment                                                ║\n";
    echo "║    - The root cause analysis was incorrect                                    ║\n";
    echo "╚════════════════════════════════════════════════════════════════════════════════╝\n";
}

echo "\n";
exit($tests_failed > 0 ? 1 : 0);
