import os
import sys
import subprocess

def check_file_exists(path):
    if not os.path.exists(path):
        print(f"❌ File not found: {path}")
        sys.exit(1)

def run_cmd(command):
    print(f"⚙️  Running: {command}")
    result = subprocess.run(command, shell=True)
    if result.returncode != 0:
        print(f"❌ Command failed: {command}")
        sys.exit(1)
