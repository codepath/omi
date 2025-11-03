# ADB Server Startup Script for Port 5038
# This script ensures ADB starts on port 5038 instead of the default 5037

Write-Host "Starting ADB Server on port 5038..." -ForegroundColor Green

# Set the environment variable for this session
$env:ANDROID_ADB_SERVER_PORT = "5038"

# Kill any existing ADB server
Write-Host "Stopping any existing ADB server..." -ForegroundColor Yellow
adb kill-server 2>$null

# Start ADB server on port 5038
Write-Host "Starting ADB server on port 5038..." -ForegroundColor Yellow
adb start-server

# Check if server started successfully
Write-Host "Testing ADB connection..." -ForegroundColor Yellow
$devices = adb devices 2>$null

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ ADB Server started successfully on port 5038" -ForegroundColor Green
    Write-Host "You can now use 'adb' commands normally" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Connected devices:" -ForegroundColor Cyan
    adb devices
} else {
    Write-Host "❌ Failed to start ADB server" -ForegroundColor Red
    Write-Host "Please check your ADB installation and try again" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")