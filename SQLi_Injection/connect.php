<?php
$hostname = "localhost";
$username = "root";
$password = "";
$dbname = "user_db";

// Establish database connection
$conn = mysqli_connect($hostname, $username, $password, $dbname);

// Check connection
if (mysqli_connect_errno()) {
    // Log error securely without exposing details to users
    error_log("Database connection failed: " . mysqli_connect_error());
    
    // Display generic error message to user
    die("An error occurred while connecting to the database. Please try again later.");
}

// Set character set to utf8mb4 for security and proper character handling
if (!mysqli_set_charset($conn, "utf8mb4")) {
    error_log("Error setting character set utf8mb4: " . mysqli_error($conn));
}

?>
