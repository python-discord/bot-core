# WARNING: This file must remain compatible with python 3.8

# This script performs all the actions required to build and deploy our project on netlify
# It depends on the following packages, which are set in the netlify UI:
# httpx == 0.19.0

import importlib
from pathlib import Path

import httpx

SCRIPT_SOURCE = "https://raw.githubusercontent.com/python-discord/site/main/static-builds/netlify_build.py"
OUTPUT = Path("docs/build.py")
OUTPUT.unlink(missing_ok=True)

build_script = httpx.get(SCRIPT_SOURCE)
build_script.raise_for_status()
OUTPUT.write_text(
    build_script.text.replace(
        "Build & Publish Static Preview",
        "Build Docs"
    ).replace(
        "static-build",
        "docs"
    )
)

script = importlib.import_module(OUTPUT.name.replace(".py", "").replace("/", "."))

if __name__ == "__main__":
    print("Build started")
    script.download_artifact(*script.get_build_artifact())
