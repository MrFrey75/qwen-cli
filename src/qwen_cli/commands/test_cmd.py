import sys
import subprocess


def cmd_test(args):
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", "-v"], check=False)
        return result.returncode
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest")
        return 1


