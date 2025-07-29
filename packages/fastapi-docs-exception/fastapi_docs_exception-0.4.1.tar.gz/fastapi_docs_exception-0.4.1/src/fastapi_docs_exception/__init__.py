from fastapi_docs_exception.handler import ExceptionResponseFactory


def lint():  # pragma: no cover
    """Development lint function."""
    import subprocess

    subprocess.run(["ruff", "format", "."], check=True)
    subprocess.run(["ruff", "check", ".", "--fix"], check=True)
    subprocess.run(["ty", "check", "."], check=True)


__all__ = ["ExceptionResponseFactory"]
