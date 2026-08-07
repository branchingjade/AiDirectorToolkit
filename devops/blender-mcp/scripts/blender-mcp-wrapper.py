"""Wrapper to run blender-mcp MCP server with clean environment and UTF-8 output.

Usage (Hermes MCP add):
  hermes mcp add blender-mcp \
    --command "C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe" \
    --args "-s" "-E" "C:\Users\<user>\Documents\Hermes\scripts\blender-mcp-wrapper.py"
"""
import os
import sys
import io

# Force UTF-8 for stdout/stderr (avoids encoding errors with Chinese Windows error messages)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Clear PYTHONPATH to avoid picking up Hermes venv packages
# (-s -E flags on command line already handle this, but keep as belt+suspenders)
if 'PYTHONPATH' in os.environ:
    del os.environ['PYTHONPATH']
if 'PYTHONHOME' in os.environ:
    del os.environ['PYTHONHOME']

from blender_mcp.server import main
main()
