"""
Progress tracker for file transfers
"""

import sys

class ProgressTracker:
    def __init__(self, total, filename):
        self.total = total
        self.filename = filename
        self.current = 0
    def update(self, amount):
        self.current += amount
        percent = (self.current / self.total) * 100
        sys.stdout.write(f"\r[✓] {self.filename}: {percent:.1f}% ({self.current}/{self.total} bytes)")
        sys.stdout.flush()
        if self.current >= self.total:
            print()
