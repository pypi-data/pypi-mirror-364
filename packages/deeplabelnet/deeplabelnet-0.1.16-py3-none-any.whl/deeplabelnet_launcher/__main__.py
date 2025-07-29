import os
import subprocess
import sys

def run():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    manage_py = os.path.join(base_dir, "manage.py")

    if not os.path.exists(manage_py):
        print(f"manage.py not found at {manage_py}")
        sys.exit(1)

    os.chdir(base_dir)

    subprocess.run([sys.executable, manage_py, "runserver"])

if __name__ == "__main__":
    run()
