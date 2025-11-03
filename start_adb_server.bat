@echo off
REM ADB Server Startup Script for Port 5038
REM This script ensures ADB starts on port 5038 instead of the default 5037

echo Starting ADB Server on port 5038...

REM Set the environment variable for this session
set ANDROID_ADB_SERVER_PORT=5038

REM Kill any existing ADB server
adb kill-server >nul 2>&1

REM Start ADB server on port 5038
adb start-server

REM Check if server started successfully
adb devices >nul 2>&1
if %errorlevel% equ 0 (
    echo ADB Server started successfully on port 5038
    echo You can now use 'adb' commands normally
) else (
    echo Failed to start ADB server
    pause
)

echo.
echo Press any key to exit...
pause >nul