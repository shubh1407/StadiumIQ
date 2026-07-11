#!/usr/bin/env python3
"""
StadiumIQ - Streamlit Launch Wrapper
Sanitizes command-line arguments to handle platform-specific port flags.
"""

import sys
import subprocess

def main() -> None:
    # Filter out --port or -p options that can be automatically appended by the container runner
    filtered_args = []
    skip_next = False
    
    for arg in sys.argv[1:]:
        if skip_next:
            skip_next = False
            continue
        if arg in ("--port", "-p", "--host", "-h"):
            skip_next = True
            continue
        if arg.startswith("--port=") or arg.startswith("--host="):
            continue
        filtered_args.append(arg)

    # Reconstruct Streamlit command line
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        "app.py",
        "--server.port=5000",
        "--server.address=0.0.0.0",
        "--server.headless=true",
        "--server.enableCORS=false",
        "--server.enableXsrfProtection=false",
        "--server.enableWebsocketCompression=false",
        "--browser.gatherUsageStats=false"
    ] + filtered_args

    print(f"Starting Streamlit: {' '.join(cmd)}")
    sys.exit(subprocess.run(cmd).returncode)

if __name__ == "__main__":
    main()
