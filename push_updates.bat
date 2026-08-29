@echo off
echo ===================================================
echo Quick Push Updates to GitHub
echo ===================================================

cd /d "%~dp0"

set /p commit_msg="Enter commit message (or press ENTER for default): "
if "%commit_msg%"=="" (
    set commit_msg=Update Library Management System
)

git add .
git commit -m "%commit_msg%"
git push origin main

if errorlevel 1 (
    echo.
    echo [ERROR] Push failed. Make sure you are connected to the internet and authenticated.
) else (
    echo.
    echo [SUCCESS] Updates pushed to GitHub successfully!
)

pause
