@echo off
echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║           SQL Injection Prevention Project - Automated Setup                   ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.
echo This script will help you complete the final setup steps.
echo.

:check_location
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Step 1: Checking Project Location
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

set "current_dir=%cd%"
echo Current directory: %current_dir%
echo.

if not exist "index.html" (
    echo ✗ ERROR: index.html not found!
    echo.
    echo This script must be run from the SQLi_Injection project folder.
    echo Please navigate to the project folder and try again.
    echo.
    pause
    exit /b 1
)

echo ✓ Project files found
echo.

:check_php
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Step 2: Checking PHP Installation
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

php --version >nul 2>&1
if errorlevel 1 (
    echo ✗ PHP is not installed or not in PATH
    echo.
    echo Please install XAMPP and ensure PHP is in your system PATH.
    echo Typical XAMPP PHP location: C:\xampp\php\
    echo.
    echo Would you like to continue anyway? (Y/N)
    set /p continue="Enter choice: "
    if /i not "%continue%"=="Y" exit /b 1
) else (
    echo ✓ PHP is installed
    php --version
    echo.
)

:check_composer
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Step 3: Checking Composer Installation
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

composer --version >nul 2>&1
if errorlevel 1 (
    echo ⚠ Composer is not installed
    echo.
    echo Composer is required for running tests.
    echo Download from: https://getcomposer.org/
    echo.
    echo You can skip this for now and install Composer later.
    echo.
    set "composer_installed=no"
) else (
    echo ✓ Composer is installed
    composer --version
    echo.
    set "composer_installed=yes"
)

:verify_setup
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Step 4: Running Setup Verification
echo ═══════════════════════════════════════════════════════════════════════════════
echo.

if exist "verify_setup.php" (
    echo Running verification script...
    echo.
    php verify_setup.php
    echo.
) else (
    echo ⚠ verify_setup.php not found, skipping verification
    echo.
)

:migrate_passwords
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Step 5: Password Migration
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo This step will convert plain text passwords to secure bcrypt hashes.
echo.
echo IMPORTANT: Run this ONCE after setting up the database.
echo If you've already run this, you can skip it.
echo.
set /p run_migration="Do you want to run password migration? (Y/N): "

if /i "%run_migration%"=="Y" (
    echo.
    echo Running migration...
    echo.
    if exist "migrate_passwords.php" (
        php migrate_passwords.php
        echo.
    ) else (
        echo ✗ migrate_passwords.php not found!
        echo.
    )
) else (
    echo Skipping migration.
    echo.
)

:install_dependencies
if "%composer_installed%"=="yes" (
    echo ═══════════════════════════════════════════════════════════════════════════════
    echo  Step 6: Installing Testing Dependencies
    echo ═══════════════════════════════════════════════════════════════════════════════
    echo.
    
    if exist "vendor" (
        echo ✓ Dependencies already installed (vendor folder exists)
        echo.
        set /p reinstall="Do you want to reinstall dependencies? (Y/N): "
        if /i not "%reinstall%"=="Y" goto test_application
    )
    
    echo Installing Composer dependencies...
    echo This may take a few minutes...
    echo.
    composer install
    echo.
    
    if errorlevel 1 (
        echo ⚠ Composer install encountered errors
        echo.
    ) else (
        echo ✓ Dependencies installed successfully
        echo.
    )
)

:test_application
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Step 7: Testing Application
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo The application should now be ready to use.
echo.
echo To test the application:
echo 1. Ensure XAMPP Apache and MySQL are running
echo 2. Open browser to: http://localhost/SQLi_Injection/index.html
echo 3. Login with: admin / admin123
echo.
set /p open_browser="Do you want to open the application in your browser? (Y/N): "

if /i "%open_browser%"=="Y" (
    echo.
    echo Opening application...
    start http://localhost/SQLi_Injection/index.html
    echo.
    echo ✓ Browser opened!
    echo.
)

:run_tests
if "%composer_installed%"=="yes" (
    if exist "vendor\bin\phpunit" (
        echo ═══════════════════════════════════════════════════════════════════════════════
        echo  Step 8: Running Automated Tests (Optional)
        echo ═══════════════════════════════════════════════════════════════════════════════
        echo.
        echo Would you like to run the automated test suite?
        echo This will verify that all security fixes are working correctly.
        echo.
        set /p run_tests="Run tests now? (Y/N): "
        
        if /i "%run_tests%"=="Y" (
            echo.
            echo Running all tests...
            echo.
            vendor\bin\phpunit
            echo.
            
            if errorlevel 1 (
                echo ⚠ Some tests failed. Please review the output above.
                echo.
            ) else (
                echo ✓ All tests passed!
                echo.
            )
        )
    )
)

:summary
echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║                           SETUP SUMMARY                                        ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.
echo Setup steps completed!
echo.
echo ✓ Project files verified
echo ✓ PHP installation checked
if "%composer_installed%"=="yes" (
    echo ✓ Composer available
    if exist "vendor" (
        echo ✓ Dependencies installed
    )
)
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  NEXT STEPS
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo 1. Ensure XAMPP Apache and MySQL are running
echo 2. Ensure database is imported (Database/127_0_0_1.sql)
echo 3. Open: http://localhost/SQLi_Injection/index.html
echo 4. Login with: admin / admin123
echo.
echo For detailed instructions, read: COMPLETE_SETUP.md
echo For quick start, read: START_HERE.md
echo For interactive menu, run: QUICKSTART.bat
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  TROUBLESHOOTING
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo If you encounter issues:
echo - Read COMPLETE_SETUP.md for detailed troubleshooting
echo - Run: php verify_setup.php
echo - Check XAMPP Control Panel (Apache and MySQL must be running)
echo.
pause
