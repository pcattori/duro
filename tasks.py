from pathlib import Path

from invoke import task


def _find_packages(path: Path):
    for pkg in path.iterdir():
        if pkg.is_dir() and len(list(pkg.glob("**/*.py"))) >= 1:
            yield pkg


@task
def lint(c):
    c.run("poetry run flake8 .", echo=True, pty=True)


@task
def format(c, fix=False):
    check = "" if fix else "--check"
    c.run(f"poetry run black {check} .", echo=True, pty=True)


@task
def typecheck(c):
    codebase = Path(__file__).parent

    for pkg in _find_packages(codebase):
        c.run(f"poetry run mypy --package {pkg.name}", echo=True, pty=True)
