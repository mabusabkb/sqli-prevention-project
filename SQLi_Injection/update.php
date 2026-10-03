<?php

include 'connect.php';

// Validate and sanitize the ID parameter
$id = null;
if (isset($_REQUEST['updateid'])) {
    // Validate ID is numeric
    if (is_numeric($_REQUEST['updateid']) && $_REQUEST['updateid'] > 0) {
        $id = (int)$_REQUEST['updateid'];
    } else {
        echo '<script>alert("Invalid user ID"); window.location = "show_users.php";</script>';
        exit();
    }
} else {
    header('location:show_users.php');
    exit();
}

// Fetch existing user data to pre-populate the form
$existing_user = null;
$stmt = mysqli_prepare($conn, "SELECT id, username, email, gender FROM users WHERE id = ?");
if ($stmt) {
    mysqli_stmt_bind_param($stmt, "i", $id);
    mysqli_stmt_execute($stmt);
    $result = mysqli_stmt_get_result($stmt);
    $existing_user = mysqli_fetch_assoc($result);
    mysqli_stmt_close($stmt);
    
    if (!$existing_user) {
        echo '<script>alert("User not found"); window.location = "show_users.php";</script>';
        exit();
    }
} else {
    error_log("Database error in update.php: " . mysqli_error($conn));
    echo '<script>alert("An error occurred. Please try again later."); window.location = "show_users.php";</script>';
    exit();
}

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
    
    // Validate ID
    if (!is_numeric($id) || $id <= 0) {
        $errors[] = "Invalid user ID";
    }
    
    // If validation errors exist, display them and stop
    if (!empty($errors)) {
        echo '<script>alert("' . implode('\\n', $errors) . '"); window.location = "update.php?updateid=' . $id . '";</script>';
        exit();
    }
    
    // Hash the password before storing
    $hashed_password = password_hash($pass, PASSWORD_DEFAULT);
    
    // Use prepared statement to prevent SQL injection
    $stmt = mysqli_prepare($conn, "UPDATE `users` SET `username`=?, `email`=?, `password`=?, `gender`=? WHERE id=?");
    
    if ($stmt) {
        // Bind parameters
        mysqli_stmt_bind_param($stmt, "ssssi", $uname, $email, $hashed_password, $gender, $id);
        
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
            error_log("Database error in update.php: " . mysqli_stmt_error($stmt));
            mysqli_stmt_close($stmt);
            mysqli_close($conn);
            echo '<script>alert("An error occurred while updating the user. Please try again."); window.location = "update.php?updateid=' . $id . '";</script>';
            exit();
        }
    } else {
        // Statement preparation failed - log error securely
        error_log("Database error in update.php: " . mysqli_error($conn));
        mysqli_close($conn);
        echo '<script>alert("An error occurred. Please try again later."); window.location = "update.php?updateid=' . $id . '";</script>';
        exit();
    }
}

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <!-- custom css file link -->
    <link rel="stylesheet" type="text/css" href="style1.css">
    <title>Update User's</title>
</head>

<body>
    <div class="form-container">
        <form method="post">
            <h3>Update Account</h3>
            <input type="text" name="username" required placeholder="Enter your name" autocomplete="off" value="<?php echo htmlspecialchars($existing_user['username']); ?>">
            <input type="email" name="email" required placeholder="Enter your email" value="<?php echo htmlspecialchars($existing_user['email']); ?>">
            <input type="password" name="password" required placeholder="Enter your password">
            <select name="gender" required>
                <option value="Male" <?php echo ($existing_user['gender'] === 'Male') ? 'selected' : ''; ?>>Male</option>
                <option value="Female" <?php echo ($existing_user['gender'] === 'Female') ? 'selected' : ''; ?>>Female</option>
            </select>
            <input type="submit" name="submit" value="Update" class="form-btn">
            <p>already have an account? <a href="index.html">login now</a></p>
        </form>
    </div>
</body>
</html>
