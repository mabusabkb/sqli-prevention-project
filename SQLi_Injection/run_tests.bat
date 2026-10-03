@echo off
REM Bug Condition Exploration Test Runner for Windows
REM This script runs the bug condition exploration tests

echo.
echo ================================================================================
echo   Bug Condition Exploration Tests
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
echo Running bug condition exploration tests...
echo.
php tests/run_bug_exploration_tests.php

REM Capture exit code
set TEST_EXIT_CODE=%ERRORLEVEL%

echo.
echo ================================================================================
echo   Test Execution Complete
echo ================================================================================
echo.

if %TEST_EXIT_CODE% NEQ 0 (
    echo Tests FAILED - This is EXPECTED on unfixed code
    echo Failures confirm that vulnerabilities exist
    echo.
    echo Next steps:
    echo   1. Review the counterexamples above
    echo   2. Document the vulnerabilities found
    echo   3. Proceed to implement security fixes (Task 3)
) else (
    echo Tests PASSED - This is UNEXPECTED on unfixed code
    echo.
    echo This suggests either:
    echo   - The code is already fixed
    echo   - The tests need adjustment
    echo   - The root cause analysis was incorrect
)

echo.
pause
exit /b %TEST_EXIT_CODE%
