from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class BaseError(HTTPException):
    """Base class for all custom exceptions"""
    def __init__(
        self,
        status_code: int,
        message: str,
        error_code: str,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "error_code": error_code,
                "message": message,
                "details": details or {}
            }
        )


class NotFoundError(BaseError):
    """Resource not found error"""
    def __init__(self, resource: str, identifier: Any):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            message=f"{resource} with identifier {identifier} was not found",
            error_code="RESOURCE_NOT_FOUND",
            details={"resource": resource, "identifier": str(identifier)}
        )


class ValidationError(BaseError):
    """Response validation error"""
    def __init__(self,  message: str = "RESPONSE_VALIDATION failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Response validation failed",
            error_code="RESPONSE_VALIDATION_ERROR",
            details=details
        )

class AuthenticationError(BaseError):
    """Authentication related errors"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details

        )


class PermissionError(BaseError):
    """Permission related errors"""
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            message=message,
            error_code="PERMISSION_DENIED",
            details=details

        )


class AddressError(BaseError):
    """Address related errors"""
    def __init__(self, message: str, error_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            error_code=f"ADDRESS_{error_type}",
            details=details
        )



class AddressesError(BaseError):
    """Addresses related errors"""
    def __init__(self, message: str, error_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST, 
            message=message,
            error_code=f"ADDRESSES_{error_type}",
            details=details
        )



class CustomerError(BaseError):
    """Customer related errors"""
    def __init__(self, message: str, error_type: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            message=message,
            error_code=f"CUSTOMER_{error_type}",
            details=details
        ) 



