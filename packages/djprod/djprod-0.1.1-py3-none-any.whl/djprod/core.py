import sys
import shutil
from pathlib import Path
from djprod.utils import (
    # info,
    error,
    success,
    run_cmd,
    print_project_info,
    replace_postgres_with_sqlite
)

def create_project(project_name: str, use_local: bool = False, verbose: bool = False):
    current_dir = Path(__file__).resolve().parent.parent
    templates_dir = current_dir / "templates"
    dest_path = Path.cwd() / project_name

    if dest_path.exists():
        error(f"Project already exists `[bold]{project_name}[/]`")
        sys.exit(1)

    shutil.copytree(templates_dir, dest_path)
    success(f"Project '{project_name}' created at {dest_path}")

    if use_local:
        base_py = dest_path / "core" / "django" / "base.py"
        replace_postgres_with_sqlite(base_py)

    run_cmd("uv init .", verbose=verbose, cwd=dest_path)

    deps = [
        "django",
        "django-environ",
        "psycopg2-binary" if not use_local else ""
    ]
    dep_str = " ".join(filter(None, deps))
    run_cmd(f"uv add {dep_str}", verbose=verbose, cwd=dest_path)

    print_project_info(use_local=use_local)
