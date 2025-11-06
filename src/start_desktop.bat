@echo off
title Enterprise Compliance Filter - Desktop
echo.
echo ╔══════════════════════════════════════════════════════════════╗
echo ║              🔐 ENTERPRISE COMPLIANCE FILTER                 ║
echo ║                     Desktop Edition                          ║
echo ╚══════════════════════════════════════════════════════════════╝
echo.
echo 🚀 Starting Enterprise Compliance Filter...
echo 🌐 Will open browser automatically at http://localhost:5000
echo 🔧 Press Ctrl+C to stop the server
echo.

REM Set environment file
set FLASK_ENV=development

REM Run the application
python authenticated_demo_ui.py

echo.
echo 👋 Enterprise Compliance Filter stopped
pause
