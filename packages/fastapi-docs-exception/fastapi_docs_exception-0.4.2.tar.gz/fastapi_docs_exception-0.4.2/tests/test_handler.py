import importlib

import pytest
from fastapi import HTTPException
from pydantic import Field, BaseModel

from fastapi_docs_exception.handler import (
    get_description_from_exception,
    ExceptionResponseFactory,
)


class SchemaAPIException(BaseModel):
    """Test schema for API exceptions."""

    error: str = Field(
        ...,
        description="The error type.",
        title="error",
        examples=["ExampleError"],
    )
    detail: str = Field(
        ...,
        description="The error message.",
        title="detail",
        examples=["An error occurred while processing your request."],
    )


class ApiNotFoundException(HTTPException):
    """Custom exception for API not found errors in FastAPI.

    Args:
        detail (str): A message describing the error. Defaults to "API key not found or invalid".
    """

    def __init__(self, detail: str = "API key not found or invalid"):
        super().__init__(status_code=404, detail=detail)


class NotFoundError(HTTPException):
    """Custom exception for not found errors in FastAPI."""

    def __init__(self, detail: str = "Resource not found in the storage"):
        super().__init__(status_code=404, detail=detail)


class InternalServerError(HTTPException):
    def __init__(self, detail: str = "Internal server error, please try again later"):
        super().__init__(status_code=500, detail=detail)


@pytest.mark.parametrize(
    "import_path",
    ["fastapi_docs_exception.ExceptionResponseFactory"],
)
def test_import_redirections(import_path: str):
    module_name_1, attr_name_1 = import_path.rsplit(".", 1)
    mod1 = importlib.import_module(module_name_1)

    try:
        getattr(mod1, attr_name_1)
    except AttributeError as e:
        pytest.fail(f"Import failed for {import_path}: {e}")


@pytest.mark.parametrize(
    "exception, expected_description",
    [
        (
            ApiNotFoundException(),
            "ApiNotFoundException: Custom exception for API not found errors in FastAPI.",
        ),
        (
            NotFoundError(),
            "NotFoundError: Custom exception for not found errors in FastAPI.",
        ),
        (
            InternalServerError(),
            "InternalServerError: Internal server error, please try again later",
        ),
    ],
)
def test_get_description_from_exception(
    exception: HTTPException, expected_description: str
):
    """Test the get_description_from_exception function."""
    description = get_description_from_exception(exception)

    assert description == expected_description, (
        f"Expected: {expected_description}, but got: {description}"
    )


def test_exception_response_factory_build_multiple():
    """Test the ExceptionResponseFactory build method."""
    exc_response_factory = ExceptionResponseFactory()

    responses = exc_response_factory.build(
        [
            NotFoundError(),
            InternalServerError(),
            ApiNotFoundException(),
        ]
    )
    assert responses == {
        404: {
            "description": (
                "- NotFoundError: Custom exception for not found errors in FastAPI.\n"
                "- ApiNotFoundException: Custom exception for API not found errors in FastAPI."
            ),
            "content": {
                "application/json": {
                    "examples": {
                        "NotFoundError_0": {
                            "summary": "NotFoundError",
                            "value": {
                                "error": "NotFoundError",
                                "detail": "Resource not found in the storage",
                            },
                        },
                        "ApiNotFoundException_1": {
                            "summary": "ApiNotFoundException",
                            "value": {
                                "error": "ApiNotFoundException",
                                "detail": "API key not found or invalid",
                            },
                        },
                    }
                }
            },
        },
        500: {
            "description": "InternalServerError: Internal server error, please try again later",
            "content": {
                "application/json": {
                    "example": {
                        "error": "InternalServerError",
                        "detail": "Internal server error, please try again later",
                    }
                }
            },
        },
    }


def test_exception_response_factory_build_multiple_with_model():
    """Test the ExceptionResponseFactory build method with a model."""
    exc_response_factory = ExceptionResponseFactory(model=SchemaAPIException)

    responses = exc_response_factory.build(
        [
            NotFoundError(),
            InternalServerError(),
            ApiNotFoundException(),
        ],
    )
    assert responses[404]["model"] == SchemaAPIException
    assert responses[500]["model"] == SchemaAPIException
