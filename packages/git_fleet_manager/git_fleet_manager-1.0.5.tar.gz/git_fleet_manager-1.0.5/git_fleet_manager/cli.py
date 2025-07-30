"""
Command-line interface for git-fleet-manager
"""

import argparse
import sys
from git_fleet_manager.git_utils import (
    check_repositories_status,
    pull_repositories,
    push_repositories,
    log_repositories,
    branch_repositories,
    checkout_repositories,
)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="A command line tool for managing several git repositories at once.")

    # Add arguments here
    parser.add_argument("--version", action="store_true", help="Print version information and exit")

    parser.add_argument("command", nargs="?", help="Command to execute (status, pull, push, log, branch, checkout)")

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan for git repositories (default: current directory)",
    )

    parser.add_argument(
        "--max-commits",
        type=int,
        default=10,
        help="Maximum number of commits to display for the log command (default: 10)",
    )

    parser.add_argument(
        "--with-remote",
        action="store_true",
        help="Show remote branches in addition to local branches (for branch command)",
    )

    parser.add_argument(
        "--grep",
        type=str,
        help="Filter repositories by branch name (for branch command)",
    )

    parser.add_argument(
        "--branch",
        type=str,
        help="Branch name to checkout (for checkout command)",
    )

    args = parser.parse_args()

    if args.version:
        from git_fleet_manager import __version__

        print(f"git-fleet-manager version {__version__}")
        return 0

    # Command processing
    if args.command == "status":
        check_repositories_status(args.directory)
    elif args.command == "pull":
        pull_repositories(args.directory)
    elif args.command == "push":
        push_repositories(args.directory)
    elif args.command == "log":
        log_repositories(args.directory, args.max_commits)
    elif args.command == "branch":
        branch_repositories(args.directory, with_remote=args.with_remote, grep_branch=args.grep)
    elif args.command == "checkout":
        if not args.branch:
            print("Error: --branch argument is required for checkout command")
            return 1
        checkout_repositories(args.directory, args.branch)
    elif args.command is None:
        parser.print_help()
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
