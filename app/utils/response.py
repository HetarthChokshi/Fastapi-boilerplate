from typing import Any, Dict, List, Optional, Union
from fastapi.responses import JSONResponse


def set_response(
    status_code: int,
    data: Union[dict, list, None] = None,
    notification: str = "",
    extra: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """
    Global response builder function
    
    Args:
        status_code: HTTP status code
        data: Response data (dict or list)
        notification: Success or error message
        extra: Additional fields to include in response
    
    Returns:
        JSONResponse: Formatted JSON response
    """
    response_body = {
        "status_code": status_code,
        "message": notification,
        "data": data
    }
    
    # Add extra fields if provided
    if extra:
        response_body.update(extra)
    
    return JSONResponse(
        status_code=status_code,
        content=response_body
    )


def success_response(
    data: Union[dict, list, None] = None,
    message: str = "Success",
    extra: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Helper for success responses"""
    return set_response(200, data, message, extra)


def error_response(
    status_code: int = 400,
    message: str = "Error",
    data: Union[dict, list, None] = None,
    extra: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Helper for error responses"""
    return set_response(status_code, data, message, extra)


def created_response(
    data: Union[dict, list, None] = None,
    message: str = "Created successfully",
    extra: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Helper for creation responses"""
    return set_response(201, data, message, extra)


def not_found_response(
    message: str = "Resource not found",
    extra: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Helper for 404 responses"""
    return set_response(404, None, message, extra)


def unauthorized_response(
    message: str = "Unauthorized",
    extra: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Helper for 401 responses"""
    return set_response(401, None, message, extra)


def forbidden_response(
    message: str = "Forbidden",
    extra: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """Helper for 403 responses"""
    return set_response(403, None, message, extra)
