#!/usr/bin/env python3
"""
PolarisLLM Runtime Engine - Main Entry Point
"""

import asyncio
import logging
import sys
import argparse
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.api.server import run_server

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('polaris.log')
        ]
    )

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="PolarisLLM Runtime Engine")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=7860, help="Port to bind to")
    parser.add_argument("--log-level", default="info", help="Log level")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    
    setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("Starting PolarisLLM Runtime Engine")
    
    try:
        await run_server(
            host=args.host,
            port=args.port,
            log_level=args.log_level,
            reload=args.reload
        )
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)

def sync_main():
    """Synchronous wrapper for main"""
    asyncio.run(main())

if __name__ == "__main__":
    sync_main()