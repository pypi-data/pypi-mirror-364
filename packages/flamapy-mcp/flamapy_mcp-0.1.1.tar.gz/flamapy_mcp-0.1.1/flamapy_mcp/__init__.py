import logging
import sys
from flamapy_mcp.server import serve


def main():
    """Main entry point for the Flamapy MCP server."""
    import asyncio

    logging_level = logging.WARN

    logging.basicConfig(level=logging_level, stream=sys.stderr)
    asyncio.run(serve())


if __name__ == "__main__":
    main()
