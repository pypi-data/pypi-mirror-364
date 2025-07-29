"""
Integration Test - Tests full sender/receiver workflow
"""

import asyncio
import tempfile
import os
import sys
from pathlib import Path
import threading
import time

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.fake_sender import FakeSender
from tests.fake_receiver import FakeReceiver


class IntegrationTest:
    """Integration test for sender/receiver workflow"""
    
    def __init__(self):
        self.test_port = 9000
        self.success = False
        
    async def run_integration_test(self):
        """Run full integration test"""
        print("🔧 Starting SYSTEM-SELL Integration Test")
        print("=" * 50)
        
        # Test data
        test_content = "This is a test file for SYSTEM-SELL integration testing!\nMultiple lines of content.\n🚀 Emoji test!"
        
        try:
            # Start sender in background
            sender_task = asyncio.create_task(self.run_sender(test_content))
            
            # Wait a bit for sender to start
            await asyncio.sleep(1)
            
            # Start receiver
            receiver_task = asyncio.create_task(self.run_receiver())
            
            # Wait for both to complete
            await asyncio.gather(sender_task, receiver_task)
            
            print("\n✅ Integration test completed successfully!")
            self.success = True
            
        except Exception as e:
            print(f"\n❌ Integration test failed: {e}")
            self.success = False
    
    async def run_sender(self, test_content):
        """Run fake sender"""
        print("📤 Starting fake sender...")
        fake_sender = FakeSender(port=self.test_port)
        await fake_sender.start_fake_sender(test_file_content=test_content)
    
    async def run_receiver(self):
        """Run fake receiver"""
        print("📥 Starting fake receiver...")
        
        # Wait for sender to generate session code
        await asyncio.sleep(0.5)
        
        fake_receiver = FakeReceiver()
        
        # Use a known session code for testing
        test_session_code = "TEST1"
        
        await fake_receiver.start_fake_receiver(
            session_code=test_session_code,
            sender_host="127.0.0.1",
            sender_port=self.test_port
        )


def run_integration_test():
    """Run integration test"""
    test = IntegrationTest()
    asyncio.run(test.run_integration_test())
    return test.success


if __name__ == '__main__':
    print("🧪 SYSTEM-SELL Integration Test")
    print("=" * 40)
    
    success = run_integration_test()
    
    if success:
        print("\n🎉 Integration test passed!")
        sys.exit(0)
    else:
        print("\n💥 Integration test failed!")
        sys.exit(1)
