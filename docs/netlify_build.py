# WARNING: This file must remain compatible with python 3.8

# This script performs all the actions required to build and deploy our project on netlify
# It depends on the following packages, which are set in the netlify UI:
# httpx == 0.23.0

import subprocess
import sys
from pathlib import Path

import httpx

# Clean up environment
OUTPUT = Path("docs/build.py")
OUTPUT.unlink(missing_ok=True)

# Download and write the build script
SCRIPT_SOURCE = "https://raw.githubusercontent.com/python-discord/site/main/static-builds/netlify_build.py"
build_script = httpx.get(SCRIPT_SOURCE)
build_script.raise_for_status()
OUTPUT.write_text(build_script.text, encoding="utf-8")

if __name__ == "__main__":
    # Run the build script
    print("Build started")  # noqa: T201
    subprocess.run([sys.executable, OUTPUT.absolute()])  # noqa: S603
