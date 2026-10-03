<?php
include 'connect.php';

if(isset($_GET['deleteid'])){
    $id = $_GET['deleteid'];
    
    // Validate ID is numeric and positive
    if (!is_numeric($id) || $id <= 0) {
        error_log("Invalid delete ID attempted in delete.php: " . $id);
        echo '<script>alert("Invalid user ID"); window.location = "show_users.php";</script>';
        exit();
    }
    
    // Convert to integer for safety
    $id = (int)$id;
    
    // Use prepared statement to prevent SQL injection
    $stmt = mysqli_prepare($conn, "DELETE FROM `users` WHERE id = ?");
    
    if ($stmt) {
        // Bind parameter
        mysqli_stmt_bind_param($stmt, "i", $id);
        
        // Execute query
        $result = mysqli_stmt_execute($stmt);
        
        if($result){
            mysqli_stmt_close($stmt);
            mysqli_close($conn);
            header('location:show_users.php');
            exit();
        } else {
            // Log error securely without exposing details to user
            error_log("Database error in delete.php: " . mysqli_stmt_error($stmt));
            mysqli_stmt_close($stmt);
            mysqli_close($conn);
            echo '<script>alert("An error occurred while deleting the user. Please try again."); window.location = "show_users.php";</script>';
            exit();
        }
    } else {
        // Statement preparation failed - log error securely
        error_log("Database error in delete.php: " . mysqli_error($conn));
        mysqli_close($conn);
        echo '<script>alert("An error occurred. Please try again later."); window.location = "show_users.php";</script>';
        exit();
    }
} else {
    // No delete ID provided
    header('location:show_users.php');
    exit();
}
?>
