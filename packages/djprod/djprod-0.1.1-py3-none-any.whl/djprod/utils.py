import re
import fileinput
import subprocess
from pathlib import Path
from rich.console import Console

console = Console()

SQLITE_DB_CONFIG = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
"""

def run_cmd(cmd, verbose=False, cwd=None):
    """Run shell command silently unless verbose is True"""
    kwargs = {
        "cwd": cwd,
        "shell": True,
        "text": True
    }

    if not verbose:
        kwargs["stdout"] = subprocess.DEVNULL
        kwargs["stderr"] = subprocess.DEVNULL

    result = subprocess.run(cmd, **kwargs)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {cmd}")


def replace_postgres_with_sqlite(base_py: Path):
    """Replaces the DATABASES block with SQLite3 settings."""
    start_re = re.compile(r"^DATABASES\s*=\s*\{")
    in_block = False
    brace_level = 0

    for line in fileinput.input(base_py, inplace=True):
        if not in_block and start_re.match(line):
            in_block = True
            brace_level = line.count("{") - line.count("}")
            print(SQLITE_DB_CONFIG, end="")
            continue

        if in_block:
            brace_level += line.count("{") - line.count("}")
            if brace_level <= 0:
                in_block = False
            continue

        print(line, end='')

def info(message: str):
    console.print(f"[bold cyan]info:[/] {message}")

def success(message: str):
    console.print(f"[bold green]success:[/] {message}")

def error(message: str):
    console.print(f"[bold red]error:[/] {message}")


def print_project_info(use_local: bool = False):
    """Prints the standard project setup instructions"""
    if not use_local:
        console.print("[bold cyan]Info:[/] By default, [bold]djprod[/] uses [green]PostgreSQL[/].")
        console.print("      Use the [yellow]--local[/] flag to switch to [blue]SQLite3[/].\n")

    console.print("[bold cyan]Initialized with:[/]")
    console.print("  - [white]django[/]")
    console.print("  - [white]django-environ[/]")
    console.print("  - [white]python-environ[/]")
    if not use_local:
        console.print("  - [white]psycopg2-binary[/]")
    console.print()

    console.print("[bold cyan]Setup:[/]")
    console.print("  1. Rename [magenta].env.example[/] to [magenta].env[/]")
    console.print("  2. Paste your Django secret key into it\n")

    console.print("[bold cyan]Run:[/] [bold green]uv run manage.py runserver[/]\n")

    console.print("[bold cyan]Docs:[/] https://docs.astral.sh/uv/")
