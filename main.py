"""Main entry point for Koran Teknologi."""

import argparse
import asyncio
import sys
from cmd.cli import run_cli
from cmd.http import run_http

from dotenv import load_dotenv

from utils.logger import setup_logger

logger = setup_logger(__name__)


def parse_command() -> argparse.Namespace:
    """Parse command line arguments for the main entry point."""
    parser = argparse.ArgumentParser(
        description="Koran Teknologi - Tech Blog Aggregator"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # CLI command
    cli_parser = subparsers.add_parser("cli", help="Run in CLI mode")
    cli_parser.add_argument(
        "--days",
        type=int,
        default=1,
        help="Number of days to look back for posts (default: 1)",
    )
    cli_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't send to Telegram, just print posts",
    )

    # HTTP command
    http_parser = subparsers.add_parser("http", help="Run HTTP server")
    http_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to run HTTP server on (default: 0.0.0.0)",
    )
    http_parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run HTTP server on (default: 8000)",
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    return args


async def run_async_cli(days: int, dry_run: bool) -> int:
    """Run the CLI command asynchronously."""
    try:
        await run_cli(days=days, dry_run=dry_run)
        return 0
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


def main() -> int:
    """Main entry point for the application."""
    try:
        load_dotenv()
        args = parse_command()

        if args.command == "cli":
            return asyncio.run(run_async_cli(args.days, args.dry_run))
        elif args.command == "http":
            run_http(host=args.host, port=args.port)
            return 0

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
