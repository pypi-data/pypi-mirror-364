from enum import IntEnum
from gllm_inference.constants import HTTP_STATUS_CODE_PATTERNS as HTTP_STATUS_CODE_PATTERNS
from gllm_inference.exceptions.exceptions import BaseInvokerError as BaseInvokerError, InvokerRuntimeError as InvokerRuntimeError, ModelNotFoundError as ModelNotFoundError, ProviderAuthError as ProviderAuthError, ProviderInternalError as ProviderInternalError, ProviderInvalidArgsError as ProviderInvalidArgsError, ProviderOverloadedError as ProviderOverloadedError, ProviderRateLimitError as ProviderRateLimitError
from typing import Any

class ExtendedHTTPStatus(IntEnum):
    """HTTP status codes outside of the standard HTTPStatus enum.

    Attributes:
        SERVICE_OVERLOADED (int): HTTP status code for service overloaded.
    """
    SERVICE_OVERLOADED = 529

HTTP_STATUS_TO_EXCEPTION_MAP: dict[int, type[BaseInvokerError]]

def extract_http_status_code(response: Any) -> int | None:
    '''Extract HTTP status code from error message.

    This function extracts the HTTP status code from the error message. For example,
    if the error message is "Error code: 401 - Invalid API key", "HTTP 429 Rate limit exceeded",
    or "status: 500 Internal server error", the function will return "401", "429", or "500" respectively.

    Args:
        response: The response object or error message containing HTTP status code.
            Can be a Response object, ClientResponse object, string, or dict.

    Returns:
        The extracted HTTP status code, or None if not found.
    '''
def parse_error_message(error: Any) -> BaseInvokerError:
    """Parse error from different AI providers and return appropriate exception type.

    This function analyzes the error message and HTTP status code to determine
    the most appropriate exception type to return.

    Args:
        error: The error object or message from the AI provider.
            Can be any type that might contain HTTP status information.

    Returns:
        The appropriate exception instance based on error analysis.

    Raises:
        CancelledError: If the original error is a CancelledError.
        TimeoutError: If the original error is a TimeoutError.
        AttributeError: If the error cannot be properly parsed.
    """
