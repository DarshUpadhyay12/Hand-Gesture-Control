@echo off
REM Hand Gesture Control - Quick Launch Script
REM This batch file activates the virtual environment and runs the app

echo Starting Hand Gesture Control...
call venv\Scripts\activate.bat
python main.py
pause
