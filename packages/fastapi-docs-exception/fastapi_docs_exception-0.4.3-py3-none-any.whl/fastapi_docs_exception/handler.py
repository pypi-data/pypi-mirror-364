from abc import ABC
from collections import defaultdict
from typing import (
    Callable,
    Sequence,
    Dict,
    Any,
    Union,
    Type,
    Optional,
    List,
    TypeVar,
    Generic,
)

# If the user uses fastapi_docs_exception, it means they have installed fastapi/pydantic.
from fastapi import HTTPException
from pydantic import BaseModel

T = TypeVar("T")
E = TypeVar("E", bound=HTTPException)

OneOrMany = Union[T, List[T]]
"""Type alias for a type that can be either a single instance of T or a list of T."""


def get_description_from_exception(exc: HTTPException) -> str:
    """
    Generate a description for the exception based on its detail.

    Args:
        exc (HTTPException): The exception to generate a description for.

    Returns:
        str: A formatted description string.
    """
    # detail = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    doc = get_docstring_from_exception(exc)
    error = exc.__class__.__name__
    return f"{error}: {doc}"


def get_examples_from_exception(exc: HTTPException) -> Dict[str, Any]:
    """
    Generate an example response for the exception.

    Args:
        exc (HTTPException): The exception to generate an example for.

    Returns:
        Dict[str, Any]: A dictionary containing the example response.
    """
    return {
        "error": exc.__class__.__name__,
        "detail": exc.detail,
        # "status_code": exc.status_code,
    }


def get_docstring_from_exception(exc: HTTPException) -> str:
    """
    Generate a docstring for the exception.

    Notes:
        This function extracts the first paragraph of the exception's
        docstring, if not available, it returns the exception's detail.

    Args:
        exc (HTTPException): The exception to generate a docstring for.

    Returns:
        str: A formatted docstring string.
    """
    doc = exc.__doc__ if exc.__doc__ else ""
    return doc.split("\n\n")[0] if doc else exc.detail


class ExceptionResponseFactory(Generic[E], ABC):
    """Abstract base class for response factories.

    Notes:
        This abstract allow to another developer to use custom HTTPException system
    """

    def __init__(
        self,
        example_fn: Callable[[E], Dict[str, Any]],
        description_fn: Callable[[E], str],
        model: Optional[Type[BaseModel]] = None,
    ):
        self.example_fn = example_fn
        self.description_fn = description_fn
        self.model = model

    def build(self, exceptions: Sequence[E]) -> Dict:
        """Build the responses dict for FastAPI/OpenAPI from a list of exceptions."""
        responses = {}
        grouped = defaultdict(list)

        for exc in exceptions:
            grouped[exc.status_code].append(exc)

        for status_code, exc_list in grouped.items():
            if len(exc_list) == 1:
                exc = exc_list[0]
                responses[status_code] = self._single_response(exc)
            else:
                responses[status_code] = self._multi_response(exc_list)

            if self.model:
                responses[status_code]["model"] = self.model

        return responses

    def _single_response(self, exc: E) -> Dict[str, Any]:
        """Helper method to create a single response dict (without SelectInput on Swagger)."""
        description = self.description_fn(exc)
        examples = self.example_fn(exc)

        response: Dict = {
            "description": description,
            "content": {
                "application/json": {
                    "example": examples,
                }
            },
        }

        return response

    def _multi_response(self, exc_list: Sequence[E]) -> Dict:
        """Helper method to create a response dict for multiple exceptions (with SelectInput on Swagger)."""
        examples_block = {}
        description = "\n".join(f"- {self.description_fn(exc)}" for exc in exc_list)

        for i, exc in enumerate(exc_list):
            key = f"{exc.__class__.__name__}_{i}"
            examples_block[key] = {
                # Summary replace key with class name (like single response)
                "summary": exc.__class__.__name__,
                "value": self.example_fn(exc),
            }

        # IDK why, not typing response return typing error with BaseModel
        response: Dict = {
            "description": description,
            "content": {
                "application/json": {
                    "examples": examples_block,
                }
            },
        }

        return response


class HTTPExceptionResponseFactory(ExceptionResponseFactory[HTTPException]):
    """Construct the responses dict for FastAPI/OpenAPI from a list of HTTPException.

    Attributes:
        example_fn (Callable[[HTTPException], Dict[str, Any]]): Function to generate example responses.
        description_fn (Callable[[HTTPException], str]): Function to generate descriptions for exceptions.
        model (Optional[Type[BaseModel]]): Optional Pydantic model for response validation.
    """

    def __init__(
        self,
        example_fn: Optional[Callable[[HTTPException], Dict[str, Any]]] = None,
        description_fn: Optional[Callable[[HTTPException], str]] = None,
        model: Optional[Type[BaseModel]] = None,
    ):
        example_fn = example_fn or get_examples_from_exception
        description_fn = description_fn or get_description_from_exception

        super().__init__(
            example_fn=example_fn,
            description_fn=description_fn,
            model=model,
        )
