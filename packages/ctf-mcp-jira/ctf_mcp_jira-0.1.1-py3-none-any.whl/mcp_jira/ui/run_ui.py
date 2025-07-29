#!/usr/bin/env python3
"""
Launcher for the MCP JIRA Configuration UI
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Launch the Streamlit UI for MCP JIRA configuration."""
    # Get the path to the app.py file
    ui_dir = Path(__file__).parent
    app_path = ui_dir / "app.py"
    
    # Launch streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path)]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nConfiguration UI stopped.")
        sys.exit(0)
    except Exception as e:
        print(f"Error launching configuration UI: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()