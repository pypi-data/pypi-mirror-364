@echo off
REM Quick Test Script for SYSTEM-SELL
echo 🔧 SYSTEM-SELL Quick Test Suite
echo ================================

echo.
echo 1. Running Unit Tests...
echo --------------------------------
python tests\test_runner.py

echo.
echo 2. Testing Fake Sender (will timeout after 10 seconds)...
echo --------------------------------
timeout /t 10 python tests\fake_sender.py --content "Test from batch script!"

echo.
echo 3. Manual Testing Instructions:
echo --------------------------------
echo To test manually:
echo   Terminal 1: python tests\fake_sender.py
echo   Terminal 2: python tests\fake_receiver.py [SESSION_CODE]
echo.
echo Or use the main application:
echo   Terminal 1: python system_sell.py send path\to\file.txt
echo   Terminal 2: python system_sell.py receive [SESSION_CODE]

pause
