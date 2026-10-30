@echo off
title ArecaVision AI Platform Shutdown
color 0C
cls

echo ===============================================================================
echo            ARECAVISION AI -- GRACEFUL SYSTEM SHUTDOWN
echo ===============================================================================
echo.

echo [*] Stopping Backend Engine on port 8000...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
echo     [OK] Port 8000 released.

echo [*] Stopping Frontend Vite Server on port 5173...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }"
echo     [OK] Port 5173 released.

echo.
echo ===============================================================================
echo   [STOPPED] All ArecaVision AI background services have been terminated.
echo ===============================================================================
echo.
timeout /t 3 >nul
exit
