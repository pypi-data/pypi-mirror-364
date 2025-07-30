"""Xcode MCP Server - Model Context Protocol server for Xcode integration"""

from .__main__ import mcp, ALLOWED_FOLDERS, get_allowed_folders

def main():
    """Entry point for the xcode-mcp-server command"""
    import sys
    from .__main__ import mcp, ALLOWED_FOLDERS, get_allowed_folders
    
    # Initialize allowed folders
    global ALLOWED_FOLDERS
    ALLOWED_FOLDERS = get_allowed_folders()
    
    # Debug info
    print(f"Allowed folders: {ALLOWED_FOLDERS}", file=sys.stderr)
    
    # Run the server
    mcp.run()

__version__ = "1.0.0"
__all__ = ["mcp", "main"]