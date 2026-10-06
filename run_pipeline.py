import subprocess
import sys


steps = [
    (
        "Data Cleaning Pipeline",
        [sys.executable, "src/main.py"]
    ),
    (
        "Automated Tests",
        [sys.executable, "-m", "pytest", "-v"]
    ),
]


print("=" * 60)
print("          DATA CLEANING AUTOMATION")
print("=" * 60)


for name, command in steps:

    print()
    print(f"Running: {name}")
    print("-" * 60)

    result = subprocess.run(command)

    if result.returncode != 0:
        print()
        print(f"ERROR: {name} failed.")
        sys.exit(1)


print()
print("=" * 60)
print("      PIPELINE COMPLETED SUCCESSFULLY")
print("=" * 60)
