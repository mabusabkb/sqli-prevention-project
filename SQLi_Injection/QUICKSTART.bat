@echo off
echo ╔════════════════════════════════════════════════════════════════════════════════╗
echo ║           SQL Injection Prevention Project - Quick Start                       ║
echo ╚════════════════════════════════════════════════════════════════════════════════╝
echo.
echo This script will help you set up and run the project.
echo.

:menu
echo ═══════════════════════════════════════════════════════════════════════════════
echo  MAIN MENU
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo  1. Verify Setup (Check if everything is configured)
echo  2. Install Composer Dependencies (PHPUnit)
echo  3. Run Password Migration Script
echo  4. Run Bug Condition Tests (Security Tests)
echo  5. Run Preservation Tests (Functionality Tests)
echo  6. Run All Tests
echo  7. Open Application in Browser
echo  8. View Setup Guide
echo  9. Exit
echo.
set /p choice="Enter your choice (1-9): "

if "%choice%"=="1" goto verify
if "%choice%"=="2" goto install
if "%choice%"=="3" goto migrate
if "%choice%"=="4" goto bug_tests
if "%choice%"=="5" goto preservation_tests
if "%choice%"=="6" goto all_tests
if "%choice%"=="7" goto open_browser
if "%choice%"=="8" goto setup_guide
if "%choice%"=="9" goto end

echo Invalid choice. Please try again.
echo.
pause
cls
goto menu

:verify
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Verifying Setup...
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
php verify_setup.php
echo.
pause
cls
goto menu

:install
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Installing Composer Dependencies...
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
composer install
echo.
echo ✓ Dependencies installed successfully!
echo.
pause
cls
goto menu

:migrate
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Running Password Migration Script...
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo IMPORTANT: This will hash all plain text passwords in the database.
echo Run this ONCE after setting up the database.
echo.
set /p confirm="Continue? (Y/N): "
if /i "%confirm%" NEQ "Y" goto menu
echo.
php migrate_passwords.php
echo.
pause
cls
goto menu

:bug_tests
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Running Bug Condition Exploration Tests (Security Tests)...
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
call run_tests.bat
echo.
pause
cls
goto menu

:preservation_tests
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Running Preservation Property Tests (Functionality Tests)...
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
call run_preservation_tests.bat
echo.
pause
cls
goto menu

:all_tests
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Running All Tests...
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
vendor\bin\phpunit
echo.
pause
cls
goto menu

:open_browser
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Opening Application in Browser...
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
echo Make sure XAMPP Apache and MySQL are running!
echo.
echo Opening: http://localhost/SQLi_Injection/index.html
echo.
start http://localhost/SQLi_Injection/index.html
echo.
echo ✓ Browser opened!
echo.
pause
cls
goto menu

:setup_guide
echo.
echo ═══════════════════════════════════════════════════════════════════════════════
echo  Opening Setup Guide...
echo ═══════════════════════════════════════════════════════════════════════════════
echo.
start SETUP_GUIDE.md
echo.
echo ✓ Setup guide opened!
echo.
pause
cls
goto menu

:end
echo.
echo Thank you for using SQL Injection Prevention Project!
echo.
exit
