@echo off
title ArecaVision AI Platform Launcher
color 0A
cls

echo ===============================================================================
echo            ARECAVISION AI -- AGRICULTURAL HEALTH & DIAGNOSTIC SAAS
echo ===============================================================================
echo.

cd /d "%~dp0"

echo [1/3] Checking Backend AI Engine on port 8000...
powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Backend is already running on http://127.0.0.1:8000
) else (
    echo       [*] Launching FastAPI Backend Engine...
    start "ArecaVision Backend" /min powershell -NoProfile -Command "python -u -m uvicorn backend.main:app --host 127.0.0.1 --port 8000"
    timeout /t 3 /nobreak >nul
)

echo [2/3] Checking Frontend Vite Interface on port 5173...
powershell -NoProfile -Command "(Get-NetTCPConnection -LocalPort 5173 -ErrorAction SilentlyContinue)" >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo       [OK] Frontend is already running on http://localhost:5173
) else (
    echo       [*] Launching React 19 Frontend...
    start "ArecaVision Frontend" /min powershell -NoProfile -Command "npm --prefix frontend run dev"
    timeout /t 3 /nobreak >nul
)

echo [3/3] Launching Web Interface...
start http://localhost:5173

echo.
echo ===============================================================================
echo   [ACTIVE] ArecaVision AI is live!
echo   - Web Dashboard : http://localhost:5173
echo   - Backend API   : http://127.0.0.1:8000/docs
echo.
echo   To stop both servers at any time, run: stop_arecavision.bat
echo ===============================================================================
echo.
timeout /t 5 >nul
exit
