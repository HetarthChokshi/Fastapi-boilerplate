from typing import List, Optional, Callable
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.services.auth import AuthService
from app.models.user import User


security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    auth_service = AuthService(db)
    return auth_service.get_current_user_from_token(credentials.credentials)


def get_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    return current_user


class RequirePermissions:
    """Dependency class for checking user permissions"""
    
    def __init__(self, permissions: List[str], require_all: bool = True):
        """
        Args:
            permissions: List of required permissions
            require_all: If True, user must have ALL permissions. If False, user needs ANY permission.
        """
        self.permissions = permissions
        self.require_all = require_all
    
    def __call__(self, current_user: User = Depends(get_active_user)) -> User:
        """Check if user has required permissions"""
        # Superadmin has all permissions
        if current_user.role.name == "superadmin":
            return current_user
        
        user_permissions = current_user.get_all_permissions()
        
        if self.require_all:
            # User must have ALL required permissions
            missing_permissions = [p for p in self.permissions if p not in user_permissions]
            if missing_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Missing required permissions: {', '.join(missing_permissions)}"
                )
        else:
            # User must have at least ONE of the required permissions
            if not any(p in user_permissions for p in self.permissions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Requires one of these permissions: {', '.join(self.permissions)}"
                )
        
        return current_user


class RequireRole:
    """Dependency class for checking user role"""
    
    def __init__(self, roles: List[str]):
        """
        Args:
            roles: List of allowed roles
        """
        self.roles = roles
    
    def __call__(self, current_user: User = Depends(get_active_user)) -> User:
        """Check if user has required role"""
        if current_user.role.name not in self.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {', '.join(self.roles)}"
            )
        
        return current_user


# Convenience functions for common permission checks
def require_admin_permission():
    """Require admin permissions"""
    return RequirePermissions(["admin:manage_users", "admin:manage_roles"], require_all=False)


def require_user_read_permission():
    """Require user read permission"""
    return RequirePermissions(["users:read"])


def require_user_write_permission():
    """Require user write permission""" 
    return RequirePermissions(["users:write"])


def require_user_delete_permission():
    """Require user delete permission"""
    return RequirePermissions(["users:delete"])


def require_superadmin_role():
    """Require superadmin role"""
    return RequireRole(["superadmin"])


def require_admin_role():
    """Require admin or superadmin role"""
    return RequireRole(["admin", "superadmin"])


# Optional user dependency (doesn't raise exception if no auth)
def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """Get current user if authenticated, None otherwise"""
    if not credentials:
        return None
    
    try:
        auth_service = AuthService(db)
        return auth_service.get_current_user_from_token(credentials.credentials)
    except HTTPException:
        return None
