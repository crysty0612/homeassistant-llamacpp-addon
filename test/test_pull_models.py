import sys
import os

# Add llamacpp to path so we can import pull_models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'llamacpp')))

from pull_models import ProgressCatcher, DOWNLOAD_STATE

class DummyStderr:
    def write(self, text):
        pass
    def flush(self):
        pass

def test_progress_catcher():
    catcher = ProgressCatcher(DummyStderr())
    
    # Test case 1: Standard tqdm output
    text1 = "  10%|█         | 1.00G/10.0G [00:10<01:30, 100MB/s]"
    catcher.write(text1)
    
    assert DOWNLOAD_STATE["progress_percent"] == "10%", f"Expected 10%, got {DOWNLOAD_STATE['progress_percent']}"
    assert DOWNLOAD_STATE["speed"] == "100MB/s", f"Expected 100MB/s, got {DOWNLOAD_STATE['speed']}"
    assert DOWNLOAD_STATE["eta"] == "01:30", f"Expected 01:30, got {DOWNLOAD_STATE['eta']}"
    
    # Test case 2: Another format
    text2 = " 99%|█████████▉| 9.90G/10.0G [01:29<00:01, 105MB/s]"
    catcher.write(text2)
    
    assert DOWNLOAD_STATE["progress_percent"] == "99%"
    assert DOWNLOAD_STATE["speed"] == "105MB/s"
    assert DOWNLOAD_STATE["eta"] == "00:01"
    
    print("All ProgressCatcher tests passed successfully!")

if __name__ == "__main__":
    test_progress_catcher()
