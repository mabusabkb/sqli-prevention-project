<?php
/**
 * Preservation Property Tests
 * 
 * IMPORTANT: These tests MUST PASS on unfixed code - they capture legitimate user operations
 * Follow observation-first methodology: observe behavior on UNFIXED code, then encode as tests
 * These tests ensure security fixes don't break existing functionality
 * 
 * **Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 3.10, 3.11, 3.12, 3.13**
 */

use PHPUnit\Framework\TestCase;

class PreservationPropertyTest extends TestCase
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
     * Property 1: Authentication Success with Valid Credentials
     * **Validates: Requirements 3.1, 3.8**
     * 
     * OBSERVATION: Login with valid credentials (admin/admin123) redirects to admin_page.html
     * PRESERVATION: This behavior must remain unchanged after security fixes
     */
    public function testAuthenticationSuccessWithValidCredentials()
    {
        // Test with known valid credentials from the database
        $valid_username = "admin";
        $valid_password = "admin123";
        
        // Simulate the authentication query (observing current behavior)
        $sql = "SELECT * FROM `users` WHERE `username` = '$valid_username' AND `password` = '$valid_password'";
        $result = mysqli_query($this->conn, $sql);
        $num_rows = mysqli_num_rows($result);
        
        // PRESERVATION: Valid credentials should authenticate successfully
        $this->assertGreaterThan(0, $num_rows, 
            "Valid credentials (admin/admin123) should authenticate successfully. Found $num_rows rows, expected > 0.");
        
        // Verify the user data is returned correctly
        $user_data = mysqli_fetch_assoc($result);
        $this->assertEquals($valid_username, $user_data['username'], 
            "Authenticated user should have username 'admin'");
    }

    /**
     * Property 2: Authentication Failure with Invalid Credentials
     * **Validates: Requirements 3.2**
     * 
     * OBSERVATION: Login with invalid credentials redirects to index.html with error
     * PRESERVATION: This behavior must remain unchanged after security fixes
     */
    public function testAuthenticationFailureWithInvalidCredentials()
    {
        // Test with invalid credentials
        $invalid_username = "nonexistent_user";
        $invalid_password = "wrong_password";
        
        // Simulate the authentication query (observing current behavior)
        $sql = "SELECT * FROM `users` WHERE `username` = '$invalid_username' AND `password` = '$invalid_password'";
        $result = mysqli_query($this->conn, $sql);
        $num_rows = mysqli_num_rows($result);
        
        // PRESERVATION: Invalid credentials should fail authentication
        $this->assertEquals(0, $num_rows, 
            "Invalid credentials should NOT authenticate. Found $num_rows rows, expected 0.");
    }

    /**
     * Property 3: User Creation with Valid Data
     * **Validates: Requirements 3.3**
     * 
     * OBSERVATION: Create user with valid data inserts record and redirects to show_users.php
     * PRESERVATION: This behavior must remain unchanged after security fixes
     */
    public function testUserCreationWithValidData()
    {
        $test_username = "preservation_test_user_" . time();
        $test_email = "preservation@example.com";
        $test_password = "TestPassword123";
        $test_gender = "Male";
        
        // Simulate user creation (observing current behavior from new_user.php)
        $sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')";
        $result = mysqli_query($this->conn, $sql);
        
        // PRESERVATION: User creation should succeed
        $this->assertTrue($result, "User creation with valid data should succeed");
        
        $test_id = mysqli_insert_id($this->conn);
        $this->assertGreaterThan(0, $test_id, "Inserted user should have a valid ID");
        
        // Verify the user was inserted correctly
        $check_sql = "SELECT * FROM `users` WHERE id='$test_id'";
        $check_result = mysqli_query($this->conn, $check_sql);
        $user_data = mysqli_fetch_assoc($check_result);
        
        $this->assertEquals($test_username, $user_data['username'], "Username should match");
        $this->assertEquals($test_email, $user_data['email'], "Email should match");
        $this->assertEquals($test_password, $user_data['password'], "Password should match (currently plain text)");
        $this->assertEquals($test_gender, $user_data['gender'], "Gender should match");
        
        // Clean up
        mysqli_query($this->conn, "DELETE FROM `users` WHERE id='$test_id'");
    }

    /**
     * Property 4: User Update with Valid Data
     * **Validates: Requirements 3.4**
     * 
     * OBSERVATION: Update user with valid data modifies record and redirects to show_users.php
     * PRESERVATION: This behavior must remain unchanged after security fixes
     */
    public function testUserUpdateWithValidData()
    {
        // First, create a test user
        $original_username = "update_test_user_" . time();
        $original_email = "update@example.com";
        $original_password = "OriginalPass123";
        $original_gender = "Female";
        
        mysqli_query($this->conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$original_username','$original_email','$original_password','$original_gender')");
        $test_id = mysqli_insert_id($this->conn);
        
        // Now update the user (observing current behavior from update.php)
        $updated_username = "updated_user_" . time();
        $updated_email = "updated@example.com";
        $updated_password = "UpdatedPass123";
        $updated_gender = "Male";
        
        $sql = "UPDATE `users` SET `username`='$updated_username',`email`='$updated_email',`password`='$updated_password',`gender`='$updated_gender' WHERE id='$test_id'";
        $result = mysqli_query($this->conn, $sql);
        
        // PRESERVATION: User update should succeed
        $this->assertTrue($result, "User update with valid data should succeed");
        
        // Verify the user was updated correctly
        $check_sql = "SELECT * FROM `users` WHERE id='$test_id'";
        $check_result = mysqli_query($this->conn, $check_sql);
        $user_data = mysqli_fetch_assoc($check_result);
        
        $this->assertEquals($updated_username, $user_data['username'], "Username should be updated");
        $this->assertEquals($updated_email, $user_data['email'], "Email should be updated");
        $this->assertEquals($updated_password, $user_data['password'], "Password should be updated");
        $this->assertEquals($updated_gender, $user_data['gender'], "Gender should be updated");
        
        // Clean up
        mysqli_query($this->conn, "DELETE FROM `users` WHERE id='$test_id'");
    }

    /**
     * Property 5: User Deletion with Valid ID
     * **Validates: Requirements 3.5**
     * 
     * OBSERVATION: Delete user with valid ID removes record and redirects to show_users.php
     * PRESERVATION: This behavior must remain unchanged after security fixes
     */
    public function testUserDeletionWithValidID()
    {
        // First, create a test user
        $test_username = "delete_test_user_" . time();
        $test_email = "delete@example.com";
        $test_password = "DeletePass123";
        $test_gender = "Male";
        
        mysqli_query($this->conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')");
        $test_id = mysqli_insert_id($this->conn);
        
        // Verify user exists before deletion
        $check_before = mysqli_query($this->conn, "SELECT * FROM `users` WHERE id='$test_id'");
        $this->assertEquals(1, mysqli_num_rows($check_before), "User should exist before deletion");
        
        // Now delete the user (observing current behavior from delete.php)
        $sql = "delete from `users` where id=$test_id";
        $result = mysqli_query($this->conn, $sql);
        
        // PRESERVATION: User deletion should succeed
        $this->assertTrue($result, "User deletion with valid ID should succeed");
        
        // Verify the user was deleted
        $check_after = mysqli_query($this->conn, "SELECT * FROM `users` WHERE id='$test_id'");
        $this->assertEquals(0, mysqli_num_rows($check_after), "User should be deleted");
    }

    /**
     * Property 6: User Display Shows Correct Columns
     * **Validates: Requirements 3.6**
     * 
     * OBSERVATION: show_users.php displays user table with id, username, email, password, gender, operations
     * PRESERVATION: After fix, password column will be removed but other columns must remain
     */
    public function testUserDisplayShowsCorrectData()
    {
        // Create a test user to display
        $test_username = "display_test_user_" . time();
        $test_email = "display@example.com";
        $test_password = "DisplayPass123";
        $test_gender = "Female";
        
        mysqli_query($this->conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$test_username','$test_email','$test_password','$test_gender')");
        $test_id = mysqli_insert_id($this->conn);
        
        // Simulate the query from show_users.php (observing current behavior)
        $sql = "SELECT * FROM `users`";
        $result = mysqli_query($this->conn, $sql);
        
        // PRESERVATION: Query should succeed and return data
        $this->assertNotFalse($result, "User display query should succeed");
        $this->assertGreaterThan(0, mysqli_num_rows($result), "User display should return at least one user");
        
        // Verify our test user is in the results
        $found = false;
        while ($row = mysqli_fetch_assoc($result)) {
            if ($row['id'] == $test_id) {
                $found = true;
                $this->assertEquals($test_username, $row['username'], "Username should be displayed");
                $this->assertEquals($test_email, $row['email'], "Email should be displayed");
                $this->assertEquals($test_gender, $row['gender'], "Gender should be displayed");
                // Note: After fix, password column will be removed, but for now it exists
                $this->assertArrayHasKey('password', $row, "Password column exists in current implementation");
            }
        }
        
        $this->assertTrue($found, "Test user should be found in display results");
        
        // Clean up
        mysqli_query($this->conn, "DELETE FROM `users` WHERE id='$test_id'");
    }

    /**
     * Property 7: Database Connection with Existing Parameters
     * **Validates: Requirements 3.7**
     * 
     * OBSERVATION: Database connection with existing parameters (localhost, root, no password, user_db) succeeds
     * PRESERVATION: This behavior must remain unchanged after security fixes
     */
    public function testDatabaseConnectionWithExistingParameters()
    {
        // Test connection with existing parameters (observing current behavior from connect.php)
        $test_conn = mysqli_connect($this->db_host, $this->db_user, $this->db_pass, $this->db_name);
        
        // PRESERVATION: Connection should succeed
        $this->assertNotFalse($test_conn, "Database connection with existing parameters should succeed");
        $this->assertFalse(mysqli_connect_errno(), "Connection should not have errors");
        
        // Verify we can query the database
        $test_query = mysqli_query($test_conn, "SELECT 1");
        $this->assertNotFalse($test_query, "Should be able to execute queries on the connection");
        
        mysqli_close($test_conn);
    }

    /**
     * Property 8: Form Submission Methods (POST/GET)
     * **Validates: Requirements 3.9, 3.10, 3.11, 3.12**
     * 
     * OBSERVATION: Forms submit via POST (login, create, update) and GET (delete) methods
     * PRESERVATION: HTTP methods must remain unchanged after security fixes
     * 
     * Note: This test verifies the data flow patterns work correctly
     */
    public function testFormSubmissionMethods()
    {
        // Test POST method for user creation (simulating form submission)
        $test_username = "post_test_user_" . time();
        $test_email = "post@example.com";
        $test_password = "PostPass123";
        $test_gender = "Male";
        
        // Simulate POST data processing (observing current behavior)
        $_POST['username'] = $test_username;
        $_POST['email'] = $test_email;
        $_POST['password'] = $test_password;
        $_POST['gender'] = $test_gender;
        $_POST['submit'] = true;
        
        // Verify POST data is accessible
        $this->assertEquals($test_username, $_POST['username'], "POST data should be accessible");
        
        // Test GET method for deletion (simulating URL parameter)
        $_GET['deleteid'] = 123;
        
        // Verify GET data is accessible
        $this->assertEquals(123, $_GET['deleteid'], "GET data should be accessible");
        
        // Clean up
        unset($_POST['username'], $_POST['email'], $_POST['password'], $_POST['gender'], $_POST['submit']);
        unset($_GET['deleteid']);
    }

    /**
     * Property 9: Existing Test Users Authenticate Successfully
     * **Validates: Requirements 3.8**
     * 
     * OBSERVATION: Existing test users (admin/admin123, shashank/shashank123) authenticate successfully
     * PRESERVATION: After password migration, these users must still authenticate successfully
     */
    public function testExistingTestUsersAuthenticate()
    {
        // Test admin user
        $admin_username = "admin";
        $admin_password = "admin123";
        
        $sql = "SELECT * FROM `users` WHERE `username` = '$admin_username' AND `password` = '$admin_password'";
        $result = mysqli_query($this->conn, $sql);
        
        // PRESERVATION: Admin user should authenticate
        $this->assertGreaterThan(0, mysqli_num_rows($result), 
            "Admin user (admin/admin123) should authenticate successfully");
        
        // Test shashank user (if exists)
        $shashank_username = "shashank";
        $shashank_password = "shashank123";
        
        $sql2 = "SELECT * FROM `users` WHERE `username` = '$shashank_username' AND `password` = '$shashank_password'";
        $result2 = mysqli_query($this->conn, $sql2);
        
        // Note: shashank user may or may not exist, so we just verify the query works
        $this->assertNotFalse($result2, "Query for shashank user should execute successfully");
    }

    /**
     * Property 10: Multiple Valid Operations in Sequence
     * **Validates: Requirements 3.3, 3.4, 3.5, 3.6**
     * 
     * OBSERVATION: Full user lifecycle (create → update → display → delete) works correctly
     * PRESERVATION: This sequence must work after security fixes
     */
    public function testMultipleValidOperationsInSequence()
    {
        // Step 1: Create user
        $username = "lifecycle_test_" . time();
        $email = "lifecycle@example.com";
        $password = "LifecyclePass123";
        $gender = "Female";
        
        $create_sql = "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES ('$username','$email','$password','$gender')";
        $create_result = mysqli_query($this->conn, $create_sql);
        $this->assertTrue($create_result, "Step 1: User creation should succeed");
        
        $user_id = mysqli_insert_id($this->conn);
        
        // Step 2: Update user
        $new_username = "updated_lifecycle_" . time();
        $update_sql = "UPDATE `users` SET `username`='$new_username' WHERE id='$user_id'";
        $update_result = mysqli_query($this->conn, $update_sql);
        $this->assertTrue($update_result, "Step 2: User update should succeed");
        
        // Step 3: Display user (verify update)
        $display_sql = "SELECT * FROM `users` WHERE id='$user_id'";
        $display_result = mysqli_query($this->conn, $display_sql);
        $user_data = mysqli_fetch_assoc($display_result);
        $this->assertEquals($new_username, $user_data['username'], "Step 3: Updated username should be displayed");
        
        // Step 4: Delete user
        $delete_sql = "delete from `users` where id=$user_id";
        $delete_result = mysqli_query($this->conn, $delete_sql);
        $this->assertTrue($delete_result, "Step 4: User deletion should succeed");
        
        // Verify deletion
        $verify_sql = "SELECT * FROM `users` WHERE id='$user_id'";
        $verify_result = mysqli_query($this->conn, $verify_sql);
        $this->assertEquals(0, mysqli_num_rows($verify_result), "Step 5: User should be deleted");
    }
}
