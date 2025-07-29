#!/bin/bash
# Quick Test Script for SYSTEM-SELL (Linux/macOS)
echo "🔧 SYSTEM-SELL Quick Test Suite"
echo "================================"

echo ""
echo "1. Running Unit Tests..."
echo "--------------------------------"
python3 tests/test_runner.py

echo ""
echo "2. Testing Fake Sender (will timeout after 10 seconds)..."
echo "--------------------------------"
timeout 10s python3 tests/fake_sender.py --content "Test from bash script!" || echo "Timeout reached"

echo ""
echo "3. Manual Testing Instructions:"
echo "--------------------------------"
echo "To test manually:"
echo "  Terminal 1: python3 tests/fake_sender.py"
echo "  Terminal 2: python3 tests/fake_receiver.py [SESSION_CODE]"
echo ""
echo "Or use the main application:"
echo "  Terminal 1: python3 system_sell.py send path/to/file.txt"
echo "  Terminal 2: python3 system_sell.py receive [SESSION_CODE]"
