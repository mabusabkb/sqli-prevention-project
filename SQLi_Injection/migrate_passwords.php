<?php
/**
 * Password Migration Script
 * 
 * This script migrates existing plain text passwords to bcrypt hashes.
 * Run this ONCE after deploying the security fixes.
 * 
 * Usage: php migrate_passwords.php
 */

include 'connect.php';

echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
echo "║                    PASSWORD MIGRATION SCRIPT                                   ║\n";
echo "║                                                                                ║\n";
echo "║  This script will hash all plain text passwords in the database.              ║\n";
echo "║  Run this ONCE after deploying security fixes.                                ║\n";
echo "╚════════════════════════════════════════════════════════════════════════════════╝\n\n";

// Check if connection is successful
if (!$conn) {
    die("ERROR: Database connection failed. Please check your connection settings.\n");
}

echo "✓ Database connection established\n\n";

// Fetch all users
$stmt = mysqli_prepare($conn, "SELECT id, username, password FROM users");

if (!$stmt) {
    die("ERROR: Failed to prepare statement: " . mysqli_error($conn) . "\n");
}

mysqli_stmt_execute($stmt);
$result = mysqli_stmt_get_result($stmt);

if (!$result) {
    die("ERROR: Failed to fetch users: " . mysqli_stmt_error($stmt) . "\n");
}

$total_users = 0;
$migrated_users = 0;
$already_hashed = 0;
$errors = 0;

echo "Starting password migration...\n";
echo str_repeat("-", 80) . "\n";

while ($row = mysqli_fetch_assoc($result)) {
    $total_users++;
    $id = $row['id'];
    $username = $row['username'];
    $password = $row['password'];
    
    // Check if password is already hashed (bcrypt starts with $2y$)
    if (strpos($password, '$2y$') === 0) {
        echo "User #{$id} ({$username}): Already hashed - SKIPPED\n";
        $already_hashed++;
        continue;
    }
    
    // Password is plain text - hash it
    $hashed_password = password_hash($password, PASSWORD_DEFAULT);
    
    // Update the password
    $update_stmt = mysqli_prepare($conn, "UPDATE users SET password = ? WHERE id = ?");
    
    if ($update_stmt) {
        mysqli_stmt_bind_param($update_stmt, "si", $hashed_password, $id);
        
        if (mysqli_stmt_execute($update_stmt)) {
            echo "User #{$id} ({$username}): Password hashed successfully - MIGRATED\n";
            $migrated_users++;
        } else {
            echo "User #{$id} ({$username}): ERROR - " . mysqli_stmt_error($update_stmt) . "\n";
            $errors++;
        }
        
        mysqli_stmt_close($update_stmt);
    } else {
        echo "User #{$id} ({$username}): ERROR - Failed to prepare update statement\n";
        $errors++;
    }
}

mysqli_stmt_close($stmt);
mysqli_close($conn);

// Print summary
echo str_repeat("-", 80) . "\n";
echo "\n╔════════════════════════════════════════════════════════════════════════════════╗\n";
echo "║                           MIGRATION SUMMARY                                    ║\n";
echo "╚════════════════════════════════════════════════════════════════════════════════╝\n\n";

echo "Total users processed: {$total_users}\n";
echo "Passwords migrated: {$migrated_users}\n";
echo "Already hashed: {$already_hashed}\n";
echo "Errors: {$errors}\n\n";

if ($errors > 0) {
    echo "⚠ WARNING: Some passwords failed to migrate. Please check the errors above.\n\n";
    exit(1);
} elseif ($migrated_users > 0) {
    echo "✓ SUCCESS: All plain text passwords have been migrated to bcrypt hashes.\n";
    echo "✓ Users can now log in with their existing passwords.\n";
    echo "✓ The backward compatibility code in connection.php can be removed if desired.\n\n";
    exit(0);
} else {
    echo "✓ INFO: No passwords needed migration. All passwords are already hashed.\n\n";
    exit(0);
}
?>
