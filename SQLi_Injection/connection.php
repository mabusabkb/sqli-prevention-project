<?php
include 'connect.php';

// Check if form was submitted
if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['username']) && isset($_POST['password'])) {
    
    $uname = $_POST['username'];
    $pass = $_POST['password'];
    
    // Input validation
    if (empty($uname) || empty($pass)) {
        echo '<script>alert("Username and password are required"); window.location = "index.html";</script>';
        exit();
    }
    
    // Length validation
    if (strlen($uname) > 200 || strlen($pass) > 200) {
        echo '<script>alert("Invalid input length"); window.location = "index.html";</script>';
        exit();
    }
    
    // Use prepared statement to prevent SQL injection
    $stmt = mysqli_prepare($conn, "SELECT id, username, password FROM users WHERE username = ?");
    
    if ($stmt) {
        // Bind parameters
        mysqli_stmt_bind_param($stmt, "s", $uname);
        
        // Execute query
        mysqli_stmt_execute($stmt);
        
        // Get result
        $result = mysqli_stmt_get_result($stmt);
        
        if ($result && $row = mysqli_fetch_assoc($result)) {
            // User found, verify password
            // Check if password is hashed (bcrypt starts with $2y$)
            if (strpos($row['password'], '$2y$') === 0) {
                // Password is hashed, use password_verify()
                if (password_verify($pass, $row['password'])) {
                    // Authentication successful
                    header("location:admin_page.html");
                    exit();
                } else {
                    // Password verification failed
                    echo '<script>alert("Wrong username or password"); window.location = "index.html";</script>';
                    exit();
                }
            } else {
                // Password is plain text (backward compatibility during migration)
                if ($pass === $row['password']) {
                    // Plain text match - rehash the password immediately
                    $hashed_password = password_hash($pass, PASSWORD_DEFAULT);
                    $update_stmt = mysqli_prepare($conn, "UPDATE users SET password = ? WHERE id = ?");
                    mysqli_stmt_bind_param($update_stmt, "si", $hashed_password, $row['id']);
                    mysqli_stmt_execute($update_stmt);
                    mysqli_stmt_close($update_stmt);
                    
                    // Authentication successful
                    header("location:admin_page.html");
                    exit();
                } else {
                    // Password mismatch
                    echo '<script>alert("Wrong username or password"); window.location = "index.html";</script>';
                    exit();
                }
            }
        } else {
            // User not found
            echo '<script>alert("Wrong username or password"); window.location = "index.html";</script>';
            exit();
        }
        
        mysqli_stmt_close($stmt);
    } else {
        // Statement preparation failed - log error securely
        error_log("Database error in connection.php: " . mysqli_error($conn));
        echo '<script>alert("An error occurred. Please try again later."); window.location = "index.html";</script>';
        exit();
    }
} else {
    // Invalid request method or missing parameters
    header("location:index.html");
    exit();
}
?>