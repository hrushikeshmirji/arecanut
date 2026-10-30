@echo off
title ArecaGuard AI Engine & Frontend
echo ===================================================
echo   Starting ArecaGuard Services (Backend + Frontend)
echo ===================================================

echo [1/2] Starting FastAPI Backend on http://127.0.0.1:8000 ...
start "ArecaGuard Backend" cmd /k "python -m uvicorn main:app --host 127.0.0.1 --port 8000 --app-dir backend"

echo [2/2] Starting Vite Frontend on http://localhost:5173 ...
start "ArecaGuard Frontend" cmd /k "npm --prefix frontend run dev"

echo.
echo ===================================================
echo   Services are running!
echo   * UI:      http://localhost:5173
echo   * Backend: http://127.0.0.1:8000
echo   * Docs:    http://127.0.0.1:8000/docs
echo ===================================================
