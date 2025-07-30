# FastAPI Docs Exception

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/fastapi_docs_exception.svg)](https://pypi.org/project/fastapi_docs_exception/)
[![CI](https://github.com/Athroniaeth/fastapi-docs-exception/actions/workflows/release.yml/badge.svg)](https://github.com/Athroniaeth/fastapi-docs-exception/actions/workflows/release.yml)

> **Automatically expose your custom FastAPI exceptions in Swagger / ReDoc — with proper grouping and examples.**

---

## ✨ Features

Stop repeating `responses={...}` in every route : This lightweight utility turns your custom HTTPException subclasses into **shared, documented** OpenAPI responses — complete with example payloads.

<p align="center">
  <img src="docs/swagger.png" alt="Swagger UI screenshot that shows custom 404 & 500 error examples" width="700">
</p>

<p align="center">
  <img src="docs/redoc.png" alt="Swagger UI screenshot that shows custom 404 & 500 error examples" width="700">
</p>

- **Update docs**: Convert your `HTTPException` subclasses into shared OpenAPI responses.
- **Grouped by status code**: if you have multiple exceptions with the same status code, they will be grouped together.
- **Pydantic schema**: Provide Pydantic models or tweak JSON Schema on the fly.

---

## 🚀 Installation

```bash
# With uv (recommended)
uv add fastapi_docs_exception
```

```bash
# Or the classic way
pip install fastapi_docs_exception
```

---

## ⚡ Quickstart

```python
from fastapi import FastAPI, HTTPException
from fastapi_docs_exception import HTTPExceptionResponseFactory


# 1️⃣  Define your exceptions any way you like
class ApiNotFoundException(HTTPException):
    """Custom exception for API not found errors in FastAPI."""

    def __init__(self, detail: str = "API key not found or invalid"):
        super().__init__(status_code=404, detail=detail)


class NotFoundError(HTTPException):
    """Custom exception for not found errors in FastAPI."""

    def __init__(self, detail: str = "Resource not found in the storage"):
        super().__init__(status_code=404, detail=detail)


class InternalServerError(HTTPException):
    """Custom exception for internal server errors in FastAPI."""

    def __init__(self, detail: str = "Internal server error, please try again later"):
        super().__init__(status_code=500, detail=detail)


# 2️⃣  Feed them to the factory (classes allow more flexibility)
# You can specify Pydantic schemas, edit the JSON schema, etc.
exc_response_factory = HTTPExceptionResponseFactory()

app = FastAPI(
    responses=exc_response_factory.build([
        NotFoundError(),  # 404 response
        ApiNotFoundException(),  # 404 response (grouped with the previous one)
        InternalServerError(),  # 500 response (only one)
    ]),
)


# 3️⃣  Use your exceptions in the code
@app.get("/items/{item_id}")
def get_item(item_id: str):
    if item_id != "42":
        raise NotFoundError()
    return {"item_id": item_id}
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) and you will see the custom 404 and 500 responses in the Swagger UI and ReDoc documentation with example payloads.

---

## 🔧 Development

```bash
# Clone
git clone https://github.com/your-user/fastapi_docs_exception.git
cd fastapi_docs_exception

# Optional: create a virtual env
uv venv          # makes .venv and activates it
source .venv/bin/activate

# Install dev dependencies (test, lint, type-checking)
uv pip install -e ".[dev]"
```

### Lint, format, type-check (all in one)

```bash
# Run all lint with ruff (lint, format), ty, bandit
uv run lint
```

### Run the test-suite

```bash
# Run all tests with pytest
uv run test
```

A coverage report will be shown in the terminal and `htmlcov` will be generated in the project root.

## 🤝 Contributing

All kinds of contributions are welcome – bug reports, feature ideas, docs fixes...

1. **Fork** the repo & create your branch: `git checkout -b feat/amazing-stuff`
2. **Commit** your changes with clear messages.
3. **Run** `uv run lint && uv run test` and ensure everything stays green.
4. **Open a Pull Request** describing *why* the change is useful.

Please use `commitizen` to format your commit messages, e.g. `cz commit`

---

## 📜 License

`fastapi_docs_exception` is distributed under the **MIT License** – see [`LICENSE`](LICENSE) for details.
