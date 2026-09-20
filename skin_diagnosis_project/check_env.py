import sys
import subprocess

print("=" * 60)
print("Python Version:", sys.version)
print("Python Executable:", sys.executable)
print("=" * 60)

# Get list of installed packages
result = subprocess.run([sys.executable, '-m', 'pip', 'list'], capture_output=True, text=True)
print(result.stdout)
if result.returncode != 0:
    print("ERROR:", result.stderr)
