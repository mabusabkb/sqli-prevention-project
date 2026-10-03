<?php
/**
 * Setup Verification Script
 * 
 * This script checks if the project is properly configured and ready to run.
 * Run this before starting the application to verify everything is set up correctly.
 * 
 * Usage: php verify_setup.php
 */

echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
echo "║                    SETUP VERIFICATION SCRIPT                                   ║\n";
echo "║                                                                                ║\n";
echo "║  This script will verify your project setup and configuration.                ║\n";
echo "╚════════════════════════════════════════════════════════════════════════════════╝\n\n";

$errors = 0;
$warnings = 0;
$success = 0;

// Check 1: PHP Version
echo "Checking PHP version...\n";
$php_version = phpversion();
if (version_compare($php_version, '7.4.0', '>=')) {
    echo "  ✓ PHP version: $php_version (OK)\n";
    $success++;
} else {
    echo "  ✗ PHP version: $php_version (Requires 7.4 or higher)\n";
    $errors++;
}
echo "\n";

// Check 2: Required PHP Extensions
echo "Checking required PHP extensions...\n";
$required_extensions = ['mysqli', 'pdo', 'pdo_mysql'];
foreach ($required_extensions as $ext) {
    if (extension_loaded($ext)) {
        echo "  ✓ Extension '$ext' is loaded\n";
        $success++;
    } else {
        echo "  ✗ Extension '$ext' is NOT loaded\n";
        $errors++;
    }
}
echo "\n";

// Check 3: Database Connection File
echo "Checking database connection file...\n";
if (file_exists('connect.php')) {
    echo "  ✓ connect.php exists\n";
    $success++;
    
    // Try to include and test connection
    include 'connect.php';
    if (isset($conn) && $conn) {
        echo "  ✓ Database connection successful\n";
        $success++;
        
        // Check if user_db database exists
        $db_check = mysqli_select_db($conn, 'user_db');
        if ($db_check) {
            echo "  ✓ Database 'user_db' exists\n";
            $success++;
            
            // Check if users table exists
            $table_check = mysqli_query($conn, "SHOW TABLES LIKE 'users'");
            if ($table_check && mysqli_num_rows($table_check) > 0) {
                echo "  ✓ Table 'users' exists\n";
                $success++;
                
                // Check if users exist
                $user_check = mysqli_query($conn, "SELECT COUNT(*) as count FROM users");
                if ($user_check) {
                    $row = mysqli_fetch_assoc($user_check);
                    $user_count = $row['count'];
                    echo "  ✓ Found $user_count user(s) in database\n";
                    $success++;
                    
                    // Check if passwords are hashed
                    $pwd_check = mysqli_query($conn, "SELECT password FROM users LIMIT 1");
                    if ($pwd_check) {
                        $pwd_row = mysqli_fetch_assoc($pwd_check);
                        if (strpos($pwd_row['password'], '$2y$') === 0) {
                            echo "  ✓ Passwords are hashed (bcrypt)\n";
                            $success++;
                        } else {
                            echo "  ⚠ Passwords are NOT hashed (run migrate_passwords.php)\n";
                            $warnings++;
                        }
                    }
                }
            } else {
                echo "  ✗ Table 'users' does NOT exist\n";
                $errors++;
            }
        } else {
            echo "  ✗ Database 'user_db' does NOT exist\n";
            $errors++;
        }
        
        mysqli_close($conn);
    } else {
        echo "  ✗ Database connection FAILED\n";
        $errors++;
    }
} else {
    echo "  ✗ connect.php does NOT exist\n";
    $errors++;
}
echo "\n";

// Check 4: Required PHP Files
echo "Checking required PHP files...\n";
$required_files = [
    'connection.php',
    'new_user.php',
    'update.php',
    'delete.php',
    'show_users.php',
    'migrate_passwords.php'
];

foreach ($required_files as $file) {
    if (file_exists($file)) {
        echo "  ✓ $file exists\n";
        $success++;
    } else {
        echo "  ✗ $file does NOT exist\n";
        $errors++;
    }
}
echo "\n";

// Check 5: Required HTML Files
echo "Checking required HTML files...\n";
$required_html = [
    'index.html',
    'admin_page.html',
    'new_users.html'
];

foreach ($required_html as $file) {
    if (file_exists($file)) {
        echo "  ✓ $file exists\n";
        $success++;
    } else {
        echo "  ✗ $file does NOT exist\n";
        $errors++;
    }
}
echo "\n";

// Check 6: CSS Files
echo "Checking CSS files...\n";
$css_files = ['style.css', 'style1.css', 'style3.css'];
foreach ($css_files as $file) {
    if (file_exists($file)) {
        echo "  ✓ $file exists\n";
        $success++;
    } else {
        echo "  ⚠ $file does NOT exist (styling may be affected)\n";
        $warnings++;
    }
}
echo "\n";

// Check 7: Testing Setup
echo "Checking testing setup...\n";
if (file_exists('composer.json')) {
    echo "  ✓ composer.json exists\n";
    $success++;
    
    if (file_exists('vendor/autoload.php')) {
        echo "  ✓ Composer dependencies installed\n";
        $success++;
    } else {
        echo "  ⚠ Composer dependencies NOT installed (run: composer install)\n";
        $warnings++;
    }
} else {
    echo "  ⚠ composer.json does NOT exist\n";
    $warnings++;
}

if (file_exists('phpunit.xml')) {
    echo "  ✓ phpunit.xml exists\n";
    $success++;
} else {
    echo "  ⚠ phpunit.xml does NOT exist\n";
    $warnings++;
}

if (is_dir('tests')) {
    echo "  ✓ tests/ directory exists\n";
    $success++;
} else {
    echo "  ⚠ tests/ directory does NOT exist\n";
    $warnings++;
}
echo "\n";

// Check 8: Documentation
echo "Checking documentation...\n";
$docs = ['README.md', 'SETUP_GUIDE.md', 'HOW_TO_RUN.txt', 'START_HERE.md'];
foreach ($docs as $doc) {
    if (file_exists($doc)) {
        echo "  ✓ $doc exists\n";
        $success++;
    } else {
        echo "  ⚠ $doc does NOT exist\n";
        $warnings++;
    }
}
echo "\n";

// Summary
echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
echo "║                           VERIFICATION SUMMARY                                 ║\n";
echo "╚════════════════════════════════════════════════════════════════════════════════╝\n\n";

echo "✓ Successful checks: $success\n";
echo "⚠ Warnings: $warnings\n";
echo "✗ Errors: $errors\n\n";

if ($errors === 0 && $warnings === 0) {
    echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
    echo "║                    ✓ ALL CHECKS PASSED!                                        ║\n";
    echo "║                                                                                ║\n";
    echo "║  Your project is fully configured and ready to run!                           ║\n";
    echo "║                                                                                ║\n";
    echo "║  Next steps:                                                                   ║\n";
    echo "║  1. Open browser: http://localhost/SQLi_Injection/index.html                   ║\n";
    echo "║  2. Login with: admin / admin123                                               ║\n";
    echo "║  3. Explore the application                                                    ║\n";
    echo "╚════════════════════════════════════════════════════════════════════════════════╝\n";
    exit(0);
} elseif ($errors === 0) {
    echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
    echo "║                    ⚠ SETUP COMPLETE WITH WARNINGS                              ║\n";
    echo "║                                                                                ║\n";
    echo "║  Your project is configured but has some optional components missing.         ║\n";
    echo "║  The application will work, but some features may be limited.                 ║\n";
    echo "║                                                                                ║\n";
    echo "║  Warnings to address:                                                          ║\n";
    echo "║  - Run 'composer install' to enable testing                                    ║\n";
    echo "║  - Run 'php migrate_passwords.php' if passwords are not hashed                 ║\n";
    echo "╚════════════════════════════════════════════════════════════════════════════════╝\n";
    exit(0);
} else {
    echo "╔════════════════════════════════════════════════════════════════════════════════╗\n";
    echo "║                    ✗ SETUP INCOMPLETE                                          ║\n";
    echo "║                                                                                ║\n";
    echo "║  Your project has critical errors that must be fixed before running.          ║\n";
    echo "║                                                                                ║\n";
    echo "║  Please address the errors above and run this script again.                   ║\n";
    echo "║                                                                                ║\n";
    echo "║  Common fixes:                                                                 ║\n";
    echo "║  1. Import database: Database/127_0_0_1.sql in phpMyAdmin                      ║\n";
    echo "║  2. Start MySQL in XAMPP Control Panel                                         ║\n";
    echo "║  3. Verify all files are present                                               ║\n";
    echo "║                                                                                ║\n";
    echo "║  For help, read: SETUP_GUIDE.md                                                ║\n";
    echo "╚════════════════════════════════════════════════════════════════════════════════╝\n";
    exit(1);
}
?>
