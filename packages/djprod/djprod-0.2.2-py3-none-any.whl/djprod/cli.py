import argparse
from djprod.core import create_project
from djprod.env_checker import EnvChecker

class DjProdCLI(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(
            prog="djprod",
            description="Generate production ready Django project."
        )

        self.subparsers = self.add_subparsers(
            dest="command",
            parser_class=argparse.ArgumentParser
        )

        self._setup_subcommands()

    def _setup_subcommands(self):
        # djprod new <project_name> <flag>
        new = self.subparsers.add_parser("new", help="Create a new Django project")
        new.add_argument("project_name", help="Name of the Django project")
        new.add_argument("--local", action="store_true", help="Use SQLite instead of PostgreSQL")
        new.add_argument("--verbose", action="store_true", help="Show detailed output")

    def dispatch(self):
        args = self.parse_args()
        if not args.command:
            self.print_help()
            return

        method_name = f"handle_{args.command}"

        if hasattr(self, method_name):
            method = getattr(self, method_name)
            method(args)
        else:
            self.error(f"Unknown command: {args.command}")

    def handle_new(self, args):
        create_project(
            args.project_name,
            use_local=args.local,
            verbose=args.verbose
        )

def main():
    EnvChecker().check()
    DjProdCLI().dispatch()


if __name__ == "__main__":
    main()
