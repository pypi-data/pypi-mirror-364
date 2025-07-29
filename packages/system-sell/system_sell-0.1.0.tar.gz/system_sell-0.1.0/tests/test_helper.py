"""
Manual Testing Helper - Creates test files and provides instructions
"""

import os
import tempfile
from pathlib import Path
import json


def create_test_files():
    """Create various test files for manual testing"""
    
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)
    
    print(f"📁 Creating test files in: {test_dir.absolute()}")
    
    # Text file
    text_file = test_dir / "test.txt"
    with open(text_file, 'w') as f:
        f.write("Hello from SYSTEM-SELL!\n")
        f.write("This is a test text file.\n")
        f.write("🚀 File transfer testing in progress...\n")
    
    # JSON file
    json_file = test_dir / "data.json"
    test_data = {
        "app": "SYSTEM-SELL",
        "version": "1.0.0",
        "test": True,
        "features": ["P2P", "Encryption", "NAT Traversal"]
    }
    with open(json_file, 'w') as f:
        json.dump(test_data, f, indent=2)
    
    # Binary-like file (image data simulation)
    binary_file = test_dir / "test_image.dat"
    with open(binary_file, 'wb') as f:
        # Create some pseudo-binary data
        for i in range(1000):
            f.write(bytes([i % 256, (i * 2) % 256, (i * 3) % 256]))
    
    # Large text file
    large_file = test_dir / "large_test.txt"
    with open(large_file, 'w') as f:
        for i in range(1000):
            f.write(f"Line {i+1}: This is a large test file for SYSTEM-SELL transfer testing.\n")
    
    print(f"✅ Created test files:")
    for file in test_dir.iterdir():
        size = file.stat().st_size
        print(f"  📄 {file.name} ({size:,} bytes)")
    
    return test_dir


def print_testing_instructions():
    """Print manual testing instructions"""
    
    print("\n" + "=" * 60)
    print("🧪 MANUAL TESTING INSTRUCTIONS")
    print("=" * 60)
    
    print("\n📋 OPTION 1: Using Fake Terminals")
    print("-" * 40)
    print("1. Open Terminal 1 and run:")
    print("   python tests/fake_sender.py")
    print("   (Note the session code that appears)")
    print()
    print("2. Open Terminal 2 and run:")
    print("   python tests/fake_receiver.py [SESSION_CODE]")
    print("   (Replace [SESSION_CODE] with the code from step 1)")
    
    print("\n📋 OPTION 2: Using Main Application")
    print("-" * 40)
    print("1. Open Terminal 1 and run:")
    print("   python system_sell.py send test_files/test.txt")
    print("   (Note the session code that appears)")
    print()
    print("2. Open Terminal 2 and run:")
    print("   python system_sell.py receive [SESSION_CODE]")
    print("   (Replace [SESSION_CODE] with the code from step 1)")
    
    print("\n📋 OPTION 3: Different File Types")
    print("-" * 40)
    print("Try sending different types of files:")
    print("  python system_sell.py send test_files/data.json")
    print("  python system_sell.py send test_files/test_image.dat")
    print("  python system_sell.py send test_files/large_test.txt")
    
    print("\n📋 OPTION 4: Unit Tests")
    print("-" * 40)
    print("Run automated tests:")
    print("  python tests/test_runner.py")
    
    print("\n📋 OPTION 5: Quick Test (Windows)")
    print("-" * 40)
    print("Run the batch script:")
    print("  tests/run_tests.bat")
    
    print("\n" + "=" * 60)
    print("💡 TIPS:")
    print("- Make sure both terminals are in the project directory")
    print("- The fake sender creates temporary files automatically")
    print("- Check that cryptography is installed: pip install cryptography")
    print("- Use --verbose flag for detailed output")
    print("=" * 60)


def main():
    """Main function"""
    print("🔧 SYSTEM-SELL Testing Helper")
    print("=" * 40)
    
    # Create test files
    test_dir = create_test_files()
    
    # Print instructions
    print_testing_instructions()
    
    print(f"\n📁 Test files created in: {test_dir.absolute()}")
    print("🚀 Ready for testing!")


if __name__ == '__main__':
    main()
