import sys
import subprocess
from rich.console import Console

console = Console()

class EnvChecker:
    def __init__(self, min_python=(3, 11)):
        self.min_python = min_python

    def check(self):
        self.check_python()
        self.check_uv()

    def check_python(self):
        if sys.version_info < self.min_python:
            version_str = ".".join(map(str, self.min_python))
            console.print(f"[bold red]Error:[/bold red] Python {version_str} or higher is required.")
            sys.exit(1)

    def check_uv(self):
        if not self.is_uv_available():
            console.print("[bold yellow]Warning:[/bold yellow] `uv` is not installed or broken.")
            if self.prompt_install("Do you want to install `uv` now?"):
                self.install_uv()
            else:
                console.print("[bold red]Aborted:[/bold red] `uv` is required to continue.")
                sys.exit(1)

    def is_uv_available(self) -> bool:
        try:
            result = subprocess.run(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return result.returncode == 0
        except FileNotFoundError:
            return False

    def prompt_install(self, msg: str) -> bool:
        try:
            resp = input(f"{msg} [y/N]: ").strip().lower()
            return resp == "y"
        except KeyboardInterrupt:
            console.print("\n[bold red]Cancelled.[/bold red]")
            return False

    def install_uv(self):
        try:
            console.print("[bold green]Installing `uv`...[/bold green]")
            subprocess.run(
                "curl -Ls https://astral.sh/uv/install.sh | sh",
                shell=True,
                check=True,
                stdout=subprocess.DEVNULL,
                # stderr=subprocess.DEVNULL
            )
            console.print("[bold green]`uv` installed successfully.[/bold green]")
        except subprocess.CalledProcessError:
            console.print("[bold red]Installation failed.[/bold red] Please install `uv` manually.")
            sys.exit(1)
