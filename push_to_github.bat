@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo Pushing Library Management System to GitHub
echo Repository: https://github.com/shivamgupta13m-hue/library-management-system.git
echo ===================================================

cd /d "%~dp0"

echo [1/5] Checking Git...
git --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/downloads
    pause
    exit /b 1
)

echo [2/5] Checking Git Identity...
for /f "delims=" %%i in ('git config user.name') do set GIT_USER=%%i
for /f "delims=" %%i in ('git config user.email') do set GIT_EMAIL=%%i

if "%GIT_USER%"=="" (
    echo Git username is not set.
    set /p GIT_USER="Enter your Name or GitHub username (e.g. shivamgupta13m-hue): "
    git config --global user.name "!GIT_USER!"
)

if "%GIT_EMAIL%"=="" (
    echo Git email is not set.
    set /p GIT_EMAIL="Enter your GitHub email address: "
    git config --global user.email "!GIT_EMAIL!"
)

echo Using Git Identity:
git config user.name
git config user.email

echo.
echo [3/5] Initializing Git repository & branch...
if not exist ".git" (
    git init
)

git branch -M main
git remote remove origin >nul 2>&1
git remote add origin https://github.com/shivamgupta13m-hue/library-management-system.git

echo.
echo [4/5] Staging files and creating commit...
git add .
git commit -m "Initial commit: Complete Library Management System with DBMS backend"

echo.
echo [5/5] Pushing to GitHub (main branch)...
git push -u origin main

if errorlevel 1 (
    echo.
    echo ===================================================
    echo [PUSH FAILED OR AUTHENTICATION NEEDED]
    echo ===================================================
    echo If GitHub opened a browser window, please complete the login.
    echo.
    echo If your GitHub repo was created with an existing README/License:
    echo Run the following command in terminal:
    echo     git pull origin main --rebase
    echo     git push -u origin main
    echo ===================================================
) else (
    echo.
    echo ===================================================
    echo [SUCCESS] Your project is now live on GitHub!
    echo URL: https://github.com/shivamgupta13m-hue/library-management-system
    echo ===================================================
)

pause
