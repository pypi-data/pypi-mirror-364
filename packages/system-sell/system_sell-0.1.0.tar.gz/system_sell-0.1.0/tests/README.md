# SYSTEM-SELL Testing Infrastructure

This directory contains comprehensive testing tools for SYSTEM-SELL.

## 🧪 Test Files Overview

| File | Purpose |
|------|---------|
| `fake_sender.py` | Simulates a file sender for testing |
| `fake_receiver.py` | Simulates a file receiver for testing |
| `test_runner.py` | Unit tests for core functionality |
| `integration_test.py` | End-to-end integration testing |
| `test_helper.py` | Creates test files and provides instructions |
| `run_tests.bat` | Windows batch script for quick testing |
| `run_tests.sh` | Linux/macOS script for quick testing |

## 🚀 Quick Start Testing

### Option 1: Automated Tests
```bash
# Run all unit tests
python tests/test_runner.py

# Run integration test
python tests/integration_test.py

# Create test files and get instructions
python tests/test_helper.py
```

### Option 2: Manual Testing with Fake Terminals

**Terminal 1 (Sender):**
```bash
python tests/fake_sender.py
```
This will:
- Create a temporary test file
- Generate a session code (e.g., "ABC12")
- Wait for a receiver to connect

**Terminal 2 (Receiver):**
```bash
python tests/fake_receiver.py ABC12
```
This will:
- Connect to the sender using the session code
- Receive and decrypt the file
- Verify file integrity
- Display the received content

### Option 3: Testing with Real Files

**Terminal 1:**
```bash
python system_sell.py send path/to/your/file.txt
```

**Terminal 2:**
```bash
python system_sell.py receive SESSION_CODE
```

## 🎯 Test Scenarios

### Basic File Transfer
```bash
# Terminal 1
python tests/fake_sender.py --content "Hello World!"

# Terminal 2 (use the session code from Terminal 1)
python tests/fake_receiver.py ABC12
```

### Large File Testing
```bash
# Create test files first
python tests/test_helper.py

# Send large file
python system_sell.py send test_files/large_test.txt
```

### Different File Types
```bash
# JSON file
python system_sell.py send test_files/data.json

# Binary file
python system_sell.py send test_files/test_image.dat
```

## 🔧 Advanced Testing

### Custom Sender Options
```bash
# Custom port
python tests/fake_sender.py --port 9000

# Custom content
python tests/fake_sender.py --content "Custom test message"
```

### Custom Receiver Options
```bash
# Custom output directory
python tests/fake_receiver.py ABC12 --output ./downloads/

# Connect to custom host/port
python tests/fake_receiver.py ABC12 --host 192.168.1.100 --port 9000
```

## 🐛 Debugging

### Verbose Output
```bash
# Enable verbose logging
python system_sell.py --verbose send test.txt
python system_sell.py --verbose receive ABC12
```

### Common Issues

1. **Connection Refused**: Make sure sender is running first
2. **Invalid Session Code**: Check code format (5 uppercase alphanumeric)
3. **File Not Found**: Verify file path exists
4. **Permission Denied**: Check file/directory permissions

## 📊 Test Coverage

The test suite covers:
- ✅ File encryption/decryption
- ✅ Session code generation and validation
- ✅ Configuration loading
- ✅ Progress tracking
- ✅ File integrity verification
- ✅ Error handling
- ✅ Network communication

## 🎮 Interactive Demo

Run the complete demo:
```bash
python demo.py
```

This will:
1. Install requirements
2. Run unit tests
3. Create test files
4. Demo the fake sender
5. Show testing instructions

## 📁 Test Files

The `test_helper.py` script creates:
- `test.txt` - Simple text file
- `data.json` - JSON data file
- `test_image.dat` - Binary data file
- `large_test.txt` - Large text file (1000 lines)

## 🎯 Next Steps

1. Run `python tests/test_helper.py` to get started
2. Try the fake terminals for basic testing
3. Test with real files using the main application
4. Report any issues or improvements needed

Happy testing! 🚀
