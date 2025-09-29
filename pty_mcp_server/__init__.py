"""
PTY MCP Server Package
"""

__version__ = "3.1.0"

def run():
    """Console entry point for uvx installation"""
    import asyncio
    from .server import main
    
    asyncio.run(main())

__all__ = ["run", "__version__"]
