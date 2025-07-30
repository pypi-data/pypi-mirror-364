import argparse
from djprod.core import create_project


def main():
    parser = argparse.ArgumentParser(
        prog="djprod", description="Generate production-ready Django project scaffolding."
    )
    sub = parser.add_subparsers(dest="command")

    # djprod new
    new = sub.add_parser("new", help="Create a new Django project")
    new.add_argument("project_name", help="Name of the Django project")
    new.add_argument("--local", action="store_true", help="Use SQLite instead of PostgreSQL")
    new.add_argument("--verbose", action="store_true", help="Show detailed output")

     # djprod app
    app = sub.add_parser("app", help="Create a new Django app")
    app.add_argument("app_name", help="Name of the Django app")

    args = parser.parse_args()


    if args.command == "new":
        create_project(args.project_name, use_local=args.local, verbose=args.verbose)
    else:
        parser.print_help()
