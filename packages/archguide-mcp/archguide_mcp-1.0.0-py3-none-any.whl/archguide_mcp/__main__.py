#!/usr/bin/env python3
"""Main entry point for archguide-mcp server."""

import sys
from .server import main as server_main

def main():
    """Run the archguide MCP server."""
    try:
        server_main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()