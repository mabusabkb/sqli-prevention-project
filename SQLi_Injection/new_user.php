<?php

// php code to insert data into mysql database from new_users.html

include 'connect.php';

if(isset($_POST['submit']))
{
    $uname = trim($_POST['username']);
    $pass = $_POST['password'];
    $email = trim($_POST['email']);
    $gender = $_POST['gender'];
    
    // Input validation
    $errors = [];
    
    // Validate username
    if (empty($uname)) {
        $errors[] = "Username is required";
    } elseif (strlen($uname) > 200) {
        $errors[] = "Username is too long (max 200 characters)";
    }
    
    // Validate email
    if (empty($email)) {
        $errors[] = "Email is required";
    } elseif (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        $errors[] = "Invalid email format";
    } elseif (strlen($email) > 200) {
        $errors[] = "Email is too long (max 200 characters)";
    }
    
    // Validate password
    if (empty($pass)) {
        $errors[] = "Password is required";
    } elseif (strlen($pass) > 200) {
        $errors[] = "Password is too long (max 200 characters)";
    }
    
    // Validate gender
    if (empty($gender) || !in_array($gender, ['Male', 'Female'])) {
        $errors[] = "Invalid gender selection";
    }
    
    // If validation errors exist, display them and stop
    if (!empty($errors)) {
        echo '<script>alert("' . implode('\\n', $errors) . '"); window.location = "new_users.html";</script>';
        exit();
    }
    
    // Hash the password before storing
    $hashed_password = password_hash($pass, PASSWORD_DEFAULT);
    
    // Use prepared statement to prevent SQL injection
    $stmt = mysqli_prepare($conn, "INSERT INTO `users`(`username`, `email`, `password`, `gender`) VALUES (?, ?, ?, ?)");
    
    if ($stmt) {
        // Bind parameters
        mysqli_stmt_bind_param($stmt, "ssss", $uname, $email, $hashed_password, $gender);
        
        // Execute query
        $result = mysqli_stmt_execute($stmt);
        
        if($result)
        {
            mysqli_stmt_close($stmt);
            mysqli_close($conn);
            header('location:show_users.php');
            exit();
        } else {
            // Log error securely
            error_log("Database error in new_user.php: " . mysqli_stmt_error($stmt));
            mysqli_stmt_close($stmt);
            mysqli_close($conn);
            echo '<script>alert("An error occurred while creating the user. Please try again."); window.location = "new_users.html";</script>';
            exit();
        }
    } else {
        // Statement preparation failed - log error securely
        error_log("Database error in new_user.php: " . mysqli_error($conn));
        mysqli_close($conn);
        echo '<script>alert("An error occurred. Please try again later."); window.location = "new_users.html";</script>';
        exit();
    }
}
?>