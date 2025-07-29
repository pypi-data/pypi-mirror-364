#!/usr/bin/env python3
"""
Basic tests for jobmon CLI
"""

import subprocess
import sys
import os

def test_help_command():
    """Test that help command works"""
    try:
        result = subprocess.run([sys.executable, '-m', 'jobmon_pkg.cli', '--help'], 
                              capture_output=True, text=True, timeout=10)
        assert result.returncode == 0
        assert 'Enhanced Universal Job Monitor' in result.stdout
        print("✅ Help command test passed")
    except Exception as e:
        print(f"❌ Help command test failed: {e}")
        return False
    return True

def test_script_exists():
    """Test that the bash script exists and is executable"""
    from jobmon_pkg.cli import get_script_path
    script_path = get_script_path()
    
    if not os.path.exists(script_path):
        print(f"❌ Script not found at: {script_path}")
        return False
        
    if not os.access(script_path, os.X_OK):
        print(f"❌ Script not executable: {script_path}")
        return False
        
    print("✅ Script exists and is executable")
    return True

if __name__ == '__main__':
    print("Running jobmon tests...")
    tests_passed = 0
    tests_passed += test_script_exists()
    tests_passed += test_help_command()
    
    print(f"\nTests passed: {tests_passed}/2")
    if tests_passed == 2:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("❌ Some tests failed")
        sys.exit(1)
