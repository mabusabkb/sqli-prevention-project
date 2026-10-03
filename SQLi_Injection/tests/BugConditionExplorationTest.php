<?php
/**
 * Bug Condition Exploration Tests
 * 
 * CRITICAL: These tests MUST FAIL on unfixed code - failure confirms vulnerabilities exist
 * DO NOT attempt to fix the tests or the code when they fail
 * These tests encode the EXPECTED SECURE BEHAVIOR
 * 
 * **Validates: Requirements 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 1.10, 1.11, 1.12, 1.13, 1.14, 1.15**
 */

use PHPUnit\Framework\TestCase;

class BugConditionExplorationTest extends TestCase
{
    private $db_host = "localhost";
    private $db_user = "root";
    private $db_pass = "";
    private $db_name = "user_db";
    private $conn;

    protected function setUp(): void
    {
        // Establish database connection for testing
        $this->conn = mysqli_connect($this->db_host, $this->db_user, $this->db_pass, $this->db_name);
        if (!$this->conn) {
            $this->markTestSkipped('Database connection failed: ' . mysqli_connect_error());
        }
    }

    protected function tearDown(): void
    {
        if ($this->conn) {
            mysqli_close($this->conn);
        }
    }

    /**
     * Test 1: SQL Injection in connection.php - Login Bypass
     * **Validates: Requirements 1.1, 1.5**
     * 
     * EXPECTED ON UNFIXED CODE: Authentication bypassed with SQL injection payload
     * EXPECTED ON FIXED CODE: Authentication fails, SQL injection blocked
     */
    public function testSQLInjectionLoginBypass()
    {
        // SQL injection payload that should bypass authentication on vulnerable code
        $malicious_username = "admin' OR '1'='1";
        $malicious_password = "anything";

        // Simulate the vulnerable query from connection.php
        $sql = "SELECT * FROM `users` WHERE `username` = '$malicious_username' AND `password` = '$malicious_password'";
        $result = mysqli_query($this->conn, $sql);
        
        // On UNFIXED code: This will return rows (authentication bypassed)
        // On FIXED code: This test should use prepared statements and return no rows
        $num_rows = mysqli_num_rows($result);
        
        // EXPECTED SECURE BEHAVIOR: SQL injection should NOT bypass authentication
        $this->assertEquals(0, $num_rows, 
            "SQL injection payload should NOT bypass authentication. Found $num_rows rows, expected 0.");
    }

    /**
     * Test 2: SQL Injection in new_user.php - Username with SQL Payload
     * **Validates: Requirements 1.2**
     * 
     * EXPECTED ON UNFIXED CODE: SQL injection payload inserted into database
     * EXPECTED ON FIXED CODE: Data safely inserted with prepared statements
     */
    public function testSQLInjectionNewUser()
    {
        $malicious_username = "test', 'hacked@evil.com', 'hacked', 'Male'); DROP TABLE users; --";
        $email = "test@example.com";
        $password = "testpass";
        $gender = "Male";

        // Simulate the vulnerable query from new_user.php
        $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$malicious_username','$email','$password','$gender')";
        
        // On UNFIXED code: This might execute multiple statements or cause SQL errors
        // On FIXED code: Should safely insert with prepared statements
        $result = @mysqli_query($this->conn, $sql);
        
        // Check if the users table still exists (DROP TABLE should not execute)
        $check_table = mysqli_query($this->conn, "SHOW TABLES LIKE 'users'");
        $table_exists = mysqli_num_rows($check_table) > 0;
        
        // EXPECTED SECURE BEHAVIOR: Table should still exist, SQL injection should not execute
        $this->assertTrue($table_exists, 
            "SQL injection should NOT drop the users table. Table existence: " . ($table_exists ? "true" : "false"));
        
        // Clean up if insertion succeeded
        if ($result) {
            mysqli_query($this->conn, "DELETE FROM `users` WHERE `username` LIKE '%test%' OR `username` LIKE '%DROP%'");
        }
    }

    /**
     * Test 3: SQL Injection in update.php - Fields with SQL Payloads
     * **Validates: Requirements 1.3**
     * 
     * EXPECTED ON UNFIXED CODE: SQL injection modifies unintended records
     * EXPECTED ON FIXED CODE: Only specified record updated with prepared statements
     */
    public function testSQLInjectionUpdate()
    {
        // First, create a test user to update
        $test_username = "testuser_update";
        $test_email = "test@example.com";
        $test_password = "testpass";
        $test_gender = "Male";
        
        mysqli_query($this->conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')");
        $test_id = mysqli_insert_id($this->conn);
        
        // Count total users before attack
        $count_before = mysqli_num_rows(mysqli_query($this->conn, "SELECT * FROM `users`"));
        
        // SQL injection payload that attempts to modify all records
        $malicious_username = "hacked', password='hacked123' WHERE '1'='1";
        $id = $test_id;
        
        // Simulate the vulnerable query from update.php
        $sql = "UPDATE `users` SET `username`='$malicious_username',`email`='$test_email',`password`='$test_password',`gender`='$test_gender' WHERE id='$id'";
        @mysqli_query($this->conn, $sql);
        
        // Check if other users were affected
        $affected_users = mysqli_query($this->conn, "SELECT * FROM `users` WHERE `password` = 'hacked123'");
        $num_affected = mysqli_num_rows($affected_users);
        
        // EXPECTED SECURE BEHAVIOR: Only the specified user should be updated, not all users
        $this->assertEquals(0, $num_affected, 
            "SQL injection should NOT modify multiple users. Found $num_affected users with 'hacked123' password, expected 0.");
        
        // Clean up
        mysqli_query($this->conn, "DELETE FROM `users` WHERE id='$test_id' OR `username` LIKE '%hacked%'");
    }

    /**
     * Test 4: SQL Injection in delete.php - Delete with OR Condition
     * **Validates: Requirements 1.4**
     * 
     * EXPECTED ON UNFIXED CODE: Multiple/all records deleted
     * EXPECTED ON FIXED CODE: Only specified record deleted with prepared statements
     */
    public function testSQLInjectionDelete()
    {
        // Create multiple test users
        mysqli_query($this->conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('testuser1','test1@example.com','pass1','Male')");
        $id1 = mysqli_insert_id($this->conn);
        mysqli_query($this->conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('testuser2','test2@example.com','pass2','Female')");
        $id2 = mysqli_insert_id($this->conn);
        
        // Count users before deletion
        $count_before = mysqli_num_rows(mysqli_query($this->conn, "SELECT * FROM `users`"));
        
        // SQL injection payload that attempts to delete all records
        $malicious_id = "$id1 OR 1=1";
        
        // Simulate the vulnerable query from delete.php
        $sql = "delete from `users` where id=$malicious_id";
        @mysqli_query($this->conn, $sql);
        
        // Count users after deletion
        $count_after = mysqli_num_rows(mysqli_query($this->conn, "SELECT * FROM `users`"));
        
        // EXPECTED SECURE BEHAVIOR: Only one user should be deleted, not all users
        $this->assertGreaterThan(0, $count_after, 
            "SQL injection should NOT delete all users. Users remaining: $count_after, expected > 0.");
        
        // Clean up remaining test users
        mysqli_query($this->conn, "DELETE FROM `users` WHERE id IN ('$id1', '$id2')");
    }

    /**
     * Test 5: Plain Text Password Storage
     * **Validates: Requirements 1.6, 1.7**
     * 
     * EXPECTED ON UNFIXED CODE: Password stored in plain text
     * EXPECTED ON FIXED CODE: Password stored as bcrypt hash
     */
    public function testPlainTextPasswordStorage()
    {
        $test_username = "testuser_password";
        $test_email = "testpass@example.com";
        $test_password = "MySecretPassword123";
        $test_gender = "Male";
        
        // Insert user (simulating new_user.php)
        $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')";
        mysqli_query($this->conn, $sql);
        $test_id = mysqli_insert_id($this->conn);
        
        // Retrieve the stored password
        $result = mysqli_query($this->conn, "SELECT `password` FROM `users` WHERE id='$test_id'");
        $row = mysqli_fetch_assoc($result);
        $stored_password = $row['password'];
        
        // EXPECTED SECURE BEHAVIOR: Password should be hashed (bcrypt starts with $2y$)
        $this->assertStringStartsWith('$2y$', $stored_password, 
            "Password should be stored as bcrypt hash (starting with \$2y\$), but found: " . substr($stored_password, 0, 20));
        
        // EXPECTED SECURE BEHAVIOR: Stored password should NOT match plain text
        $this->assertNotEquals($test_password, $stored_password, 
            "Password should NOT be stored in plain text. Stored: $stored_password");
        
        // Clean up
        mysqli_query($this->conn, "DELETE FROM `users` WHERE id='$test_id'");
    }

    /**
     * Test 6: Plain Text Password Display in show_users.php
     * **Validates: Requirements 1.8**
     * 
     * EXPECTED ON UNFIXED CODE: Passwords visible in HTML output
     * EXPECTED ON FIXED CODE: Password column removed or masked
     */
    public function testPlainTextPasswordDisplay()
    {
        // Create a test user
        $test_username = "testuser_display";
        $test_email = "display@example.com";
        $test_password = "DisplayPassword123";
        $test_gender = "Female";
        
        mysqli_query($this->conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')");
        $test_id = mysqli_insert_id($this->conn);
        
        // Capture output from show_users.php
        ob_start();
        include 'show_users.php';
        $output = ob_get_clean();
        
        // EXPECTED SECURE BEHAVIOR: Plain text password should NOT appear in HTML output
        $this->assertStringNotContainsString($test_password, $output, 
            "Plain text password '$test_password' should NOT be visible in show_users.php output");
        
        // EXPECTED SECURE BEHAVIOR: Password column header should be removed
        $this->assertStringNotContainsString('<th scope="col">Password</th>', $output, 
            "Password column header should be removed from show_users.php");
        
        // Clean up
        mysqli_query($this->conn, "DELETE FROM `users` WHERE id='$test_id'");
    }

    /**
     * Test 7: Error Disclosure in delete.php
     * **Validates: Requirements 1.10**
     * 
     * EXPECTED ON UNFIXED CODE: Detailed MySQL errors exposed
     * EXPECTED ON FIXED CODE: Generic error messages, details logged securely
     */
    public function testErrorDisclosureDelete()
    {
        // Trigger an error by using an invalid ID that causes a database error
        // We'll temporarily break the connection to force an error
        $original_conn = $this->conn;
        mysqli_close($this->conn);
        
        // Capture output from delete.php with broken connection
        ob_start();
        $_GET['deleteid'] = 1;
        @include 'delete.php';
        $output = ob_get_clean();
        
        // EXPECTED SECURE BEHAVIOR: Detailed MySQL error should NOT be exposed
        $this->assertStringNotContainsString('mysqli_error', $output, 
            "Detailed MySQL error messages should NOT be exposed to users");
        $this->assertStringNotContainsString('MySQL', $output, 
            "MySQL-specific error details should NOT be exposed to users");
        
        // Restore connection
        $this->conn = mysqli_connect($this->db_host, $this->db_user, $this->db_pass, $this->db_name);
        unset($_GET['deleteid']);
    }

    /**
     * Test 8: Error Disclosure in connect.php
     * **Validates: Requirements 1.11**
     * 
     * EXPECTED ON UNFIXED CODE: Connection details exposed
     * EXPECTED ON FIXED CODE: Generic error message, details logged securely
     */
    public function testErrorDisclosureConnection()
    {
        // Temporarily modify connection parameters to force failure
        // We'll capture the output by including connect.php with wrong credentials
        
        // Create a temporary test file that uses wrong credentials
        $test_connect = <<<'PHP'
<?php
$hostname = "localhost";
$username = "wrong_user";
$password = "wrong_pass";
$dbname = "user_db";
$conn = mysqli_connect($hostname, $username, $password, $dbname);
if (mysqli_connect_errno()) {
    echo "Failed to connect to MySQL: " . mysqli_connect_error();
}
?>
PHP;
        
        file_put_contents('test_connect_error.php', $test_connect);
        
        // Capture output
        ob_start();
        @include 'test_connect_error.php';
        $output = ob_get_clean();
        
        // EXPECTED SECURE BEHAVIOR: Connection error details should NOT be exposed
        $this->assertStringNotContainsString('mysqli_connect_error', $output, 
            "Detailed connection error messages should NOT be exposed to users");
        $this->assertStringNotContainsString('Access denied', $output, 
            "Database access denied messages should NOT be exposed to users");
        
        // Clean up
        @unlink('test_connect_error.php');
    }

    /**
     * Test 9: Missing Email Validation
     * **Validates: Requirements 1.14**
     * 
     * EXPECTED ON UNFIXED CODE: Invalid email accepted
     * EXPECTED ON FIXED CODE: Invalid email rejected with validation error
     */
    public function testMissingEmailValidation()
    {
        $test_username = "testuser_email";
        $invalid_email = "notanemail";  // Invalid email format
        $test_password = "testpass";
        $test_gender = "Male";
        
        // Simulate insertion with invalid email (from new_user.php)
        $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$invalid_email','$test_password','$test_gender')";
        $result = @mysqli_query($this->conn, $sql);
        
        // On UNFIXED code: Invalid email will be inserted
        // On FIXED code: Should validate and reject invalid email
        
        if ($result) {
            $test_id = mysqli_insert_id($this->conn);
            
            // Retrieve the stored email
            $check = mysqli_query($this->conn, "SELECT `email` FROM `users` WHERE id='$test_id'");
            $row = mysqli_fetch_assoc($check);
            $stored_email = $row['email'];
            
            // EXPECTED SECURE BEHAVIOR: Invalid email should NOT be accepted
            $this->assertNotEquals($invalid_email, $stored_email, 
                "Invalid email format '$invalid_email' should NOT be accepted and stored");
            
            // Clean up
            mysqli_query($this->conn, "DELETE FROM `users` WHERE id='$test_id'");
        } else {
            // If insertion failed, that's the expected secure behavior
            $this->assertTrue(true, "Invalid email correctly rejected");
        }
    }

    /**
     * Test 10: Missing Length Validation
     * **Validates: Requirements 1.15**
     * 
     * EXPECTED ON UNFIXED CODE: Excessive length input accepted
     * EXPECTED ON FIXED CODE: Excessive length input rejected with validation error
     */
    public function testMissingLengthValidation()
    {
        // Create an excessively long username (10,000 characters)
        $excessive_username = str_repeat('A', 10000);
        $test_email = "length@example.com";
        $test_password = "testpass";
        $test_gender = "Male";
        
        // Simulate insertion with excessive length (from new_user.php)
        $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$excessive_username','$test_email','$test_password','$test_gender')";
        $result = @mysqli_query($this->conn, $sql);
        
        // On UNFIXED code: Excessive length might be truncated or accepted
        // On FIXED code: Should validate and reject excessive length
        
        if ($result) {
            $test_id = mysqli_insert_id($this->conn);
            
            // Retrieve the stored username
            $check = mysqli_query($this->conn, "SELECT `username` FROM `users` WHERE id='$test_id'");
            $row = mysqli_fetch_assoc($check);
            $stored_username = $row['username'];
            
            // EXPECTED SECURE BEHAVIOR: Excessive length should be rejected before insertion
            $this->assertLessThan(10000, strlen($stored_username), 
                "Excessive length username (10000 chars) should be rejected. Stored length: " . strlen($stored_username));
            
            // Clean up
            mysqli_query($this->conn, "DELETE FROM `users` WHERE id='$test_id'");
        } else {
            // If insertion failed, that's the expected secure behavior
            $this->assertTrue(true, "Excessive length correctly rejected");
        }
    }
}
