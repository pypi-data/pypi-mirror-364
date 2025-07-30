# djprod

### Yet another production-ready Django project.

`djprod` provides a CLI for creating Django projects with a clean structure, ready for real-world deployments. It includes preconfigured settings, static directories, and environment support.

## Features

- CLI to generate Django apps and projects
- Pre-separated settings: `base`, `local`, `production`
- `.env` support via `django-environ`
- PostgreSQL, Sentry, S3 configuration ready
- Includes basic templates and static structure

## Installation

```bash
pip install djprod
````

## Usage

```bash
djprod new myproject
cd myproject
````

Rename `env.example` to `.env`:

```bash
mv env.example .env
```

Run the project using [`uv`](https://github.com/astral-sh/uv):

```bash
uv run manage.py runserver
```
