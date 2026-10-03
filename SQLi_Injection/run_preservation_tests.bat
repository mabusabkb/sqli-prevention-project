@echo off
REM Preservation Property Test Runner for Windows
REM This script runs the preservation property tests

echo.
echo ================================================================================
echo   Preservation Property Tests
echo   SQL Injection Security Fixes
echo ================================================================================
echo.

REM Check if PHP is available
where php >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PHP is not installed or not in PATH
    echo.
    echo Please install PHP and add it to your system PATH, then try again.
    echo.
    echo Download PHP from: https://windows.php.net/download/
    echo.
    pause
    exit /b 1
)

REM Display PHP version
echo Using PHP:
php --version
echo.

REM Run the tests
echo Running preservation property tests...
echo.
php tests/run_preservation_tests.php

REM Capture exit code
set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
echo ================================================================================
echo   Test Execution Complete
echo ================================================================================
echo.

if %TEST_EXIT_CODE% EQU 0 (
    echo Tests PASSED - This is EXPECTED on unfixed code
    echo Baseline behavior captured successfully
    echo.
    echo Next steps:
    echo   1. Baseline behavior is now established
    echo   2. Proceed to implement security fixes (Task 3)
    echo   3. Re-run these tests after fixes to verify no regressions
    echo   4. Re-run bug condition tests to verify vulnerabilities are fixed
) else (
    echo Tests FAILED - This is UNEXPECTED on unfixed code
    echo.
    echo This suggests either:
    echo   - The database is not set up correctly
    echo   - Test users (admin/admin123) are missing
    echo   - The baseline behavior is different than expected
    echo.
    echo Please review the failures above and ensure:
    echo   - Database 'user_db' exists and is populated
    echo   - MySQL is running
    echo   - Connection credentials are correct
)

echo.
pause
exit /b %TEST_EXIT_CODE%

