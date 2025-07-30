import shutil
import subprocess  # nosec: B404
from fastapi_docs_exception.handler import HTTPExceptionResponseFactory


def _run_command(command: str, ci_cd: bool = False) -> None:  # pragma: no cover
    """
    Run a command in the shell.

    Args:
        command (str): The command to run.
        ci_cd (bool): If True, run the command in CI/CD mode (with raise on error).
    """
    print(f"Running command: {command}")
    list_command = command.split()

    program = list_command[0]
    path_program = shutil.which(program)

    if path_program is None:
        raise RuntimeError(
            f"Program '{program}' not found in PATH. "
            f"Please use `uv sync --dev` to install development dependencies."
        )

    list_command[0] = path_program

    try:
        subprocess.run(list_command, check=True, shell=False)  # nosec: B603
    except subprocess.CalledProcessError as e:
        print(f"Command failed with error: {e}")
        if ci_cd:
            raise e


def lint_ci():  # pragma: no cover
    """Command UV to run linters for CI/CD."""
    print("Running linters for CI/CD...")
    lint(ci_cd=True)


def test_ci():  # pragma: no cover
    """Command UV to run tests for CI/CD."""
    print("Running tests for CI/CD...")
    test(ci_cd=True)


def test(ci_cd: bool = False):  # pragma: no cover
    """Command UV to run tests for development or CI/CD."""
    list_commands = ["pytest"]

    if ci_cd:
        list_commands = ["pytest -q --cov-report=html --cov-report=xml"]

    for command in list_commands:
        _run_command(command, ci_cd=ci_cd)


def lint(ci_cd: bool = False):  # pragma: no cover
    """Command UV to run linters for development or CI/CD."""
    list_commands = [
        "ruff format .",
        "ruff check --fix .",
        "ty check .",
        "bandit -c pyproject.toml -r src -q",
    ]

    for command in list_commands:
        _run_command(command, ci_cd=ci_cd)


__all__ = ["HTTPExceptionResponseFactory"]
