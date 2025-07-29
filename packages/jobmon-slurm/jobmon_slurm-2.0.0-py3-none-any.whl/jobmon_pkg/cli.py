#!/usr/bin/env python3
"""
CLI wrapper for jobmon bash script
"""

import os
import sys
import subprocess
import pkg_resources

def get_script_path():
    """Get path to the jobmon bash script"""
    try:
        # Try to get from package data
        return pkg_resources.resource_filename('jobmon_pkg', 'scripts/jobmon.sh')
    except:
        # Fallback: look in same directory as this file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(script_dir, 'scripts', 'jobmon.sh')

def main():
    """Main entry point for jobmon command"""
    script_path = get_script_path()
    
    if not os.path.exists(script_path):
        print("❌ Error: jobmon script not found at:", script_path)
        print("Package may be corrupted. Try reinstalling:")
        print("  pip install --user --upgrade --force-reinstall jobmon-slurm")
        sys.exit(1)
    
    # Pass all arguments to bash script
    try:
        result = subprocess.run(['/bin/bash', script_path] + sys.argv[1:], 
                              check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error running jobmon: {e}")
        sys.exit(1)

def quiet_main():
    """Entry point for jq (quiet mode) command"""
    script_path = get_script_path()
    
    if not os.path.exists(script_path):
        print("❌ Error: jobmon script not found")
        sys.exit(1)
    
    # Add --quiet flag and pass other arguments
    try:
        result = subprocess.run(['/bin/bash', script_path, '--quiet'] + sys.argv[1:], 
                              check=False)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n🛑 Monitoring interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error running jobmon: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
