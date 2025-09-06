# Create API endpoints

# 1. Authentication API (app/api/auth.py)
auth_api_content = """from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserResponse
from app.services.auth import AuthService
from app.middleware.auth import get_current_user
from app.models.user import User
from app.utils.response import success_response, error_response, unauthorized_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=dict)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    \"\"\"
    Authenticate user and return JWT token
    \"\"\"
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(login_data.email, login_data.password)
    if not user:
        return unauthorized_response("Invalid email or password")
    
    # Create access token
    token = auth_service.create_access_token_for_user(user)
    
    return success_response(
        data={
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in,
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.name,
                "permissions": user.get_all_permissions()
            }
        },
        message="Login successful"
    )


@router.post("/logout", response_model=dict)
async def logout(current_user: User = Depends(get_current_user)):
    \"\"\"
    Logout user (token invalidation would be handled by client or blacklist)
    \"\"\"
    # In a production app, you might want to implement token blacklisting here
    # For now, we'll just return a success response
    return success_response(
        message=f"User {current_user.username} logged out successfully"
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    \"\"\"
    Get current authenticated user information
    \"\"\"
    user_data = UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        role_id=current_user.role_id,
        role_name=current_user.role.name,
        permissions=current_user.get_all_permissions(),
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    
    return success_response(
        data=user_data.dict(),
        message="User information retrieved successfully"
    )


@router.post("/refresh", response_model=dict)
async def refresh_token(current_user: User = Depends(get_current_user)):
    \"\"\"
    Refresh access token (generate new token with same claims)
    \"\"\"
    auth_service = AuthService(None)  # We don't need db for token creation
    token = auth_service.create_access_token_for_user(current_user)
    
    return success_response(
        data={
            "access_token": token.access_token,
            "token_type": token.token_type,
            "expires_in": token.expires_in
        },
        message="Token refreshed successfully"
    )
"""

with open('app/api/auth.py', 'w') as f:
    f.write(auth_api_content)

# 2. Users API (app/api/users.py)
users_api_content = """from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.base import get_db
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, UserListResponse, RoleResponse
)
from app.services.user import UserService
from app.middleware.auth import (
    require_user_read_permission,
    require_user_write_permission,
    require_user_delete_permission,
    require_admin_permission,
    get_current_user
)
from app.models.user import User
from app.utils.response import (
    success_response, error_response, created_response,
    not_found_response, forbidden_response
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("", response_model=dict)
async def get_users(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    search: Optional[str] = Query(None, description="Search in username and email"),
    role_id: Optional[int] = Query(None, description="Filter by role ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    current_user: User = Depends(require_user_read_permission()),
    db: Session = Depends(get_db)
):
    \"\"\"
    Get list of users with filtering and pagination
    Requires 'users:read' permission
    \"\"\"
    user_service = UserService(db)
    
    result = user_service.get_users(
        skip=skip,
        limit=limit,
        search=search,
        role_id=role_id,
        is_active=is_active
    )
    
    return success_response(
        data=result.dict(),
        message="Users retrieved successfully"
    )


@router.post("", response_model=dict)
async def create_user(
    user_create: UserCreate,
    current_user: User = Depends(require_user_write_permission()),
    db: Session = Depends(get_db)
):
    \"\"\"
    Create new user
    Requires 'users:write' permission
    \"\"\"
    user_service = UserService(db)
    
    try:
        new_user = user_service.create_user(user_create)
        
        user_response = UserResponse(
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            is_active=new_user.is_active,
            role_id=new_user.role_id,
            role_name=new_user.role.name,
            permissions=new_user.get_all_permissions(),
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
        
        return created_response(
            data=user_response.dict(),
            message="User created successfully"
        )
    
    except HTTPException as e:
        return error_response(
            status_code=e.status_code,
            message=e.detail
        )


@router.get("/{user_id}", response_model=dict)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_user_read_permission()),
    db: Session = Depends(get_db)
):
    \"\"\"
    Get user by ID
    Requires 'users:read' permission
    \"\"\"
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    if not user:
        return not_found_response("User not found")
    
    user_response = UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        role_id=user.role_id,
        role_name=user.role.name,
        permissions=user.get_all_permissions(),
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    
    return success_response(
        data=user_response.dict(),
        message="User retrieved successfully"
    )


@router.put("/{user_id}", response_model=dict)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    current_user: User = Depends(require_user_write_permission()),
    db: Session = Depends(get_db)
):
    \"\"\"
    Update user
    Requires 'users:write' permission
    \"\"\"
    user_service = UserService(db)
    
    try:
        updated_user = user_service.update_user(user_id, user_update)
        
        if not updated_user:
            return not_found_response("User not found")
        
        user_response = UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email,
            is_active=updated_user.is_active,
            role_id=updated_user.role_id,
            role_name=updated_user.role.name,
            permissions=updated_user.get_all_permissions(),
            created_at=updated_user.created_at,
            updated_at=updated_user.updated_at
        )
        
        return success_response(
            data=user_response.dict(),
            message="User updated successfully"
        )
    
    except HTTPException as e:
        return error_response(
            status_code=e.status_code,
            message=e.detail
        )


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_user_delete_permission()),
    db: Session = Depends(get_db)
):
    \"\"\"
    Soft delete user (set is_active to False)
    Requires 'users:delete' permission
    \"\"\"
    # Prevent self-deletion
    if current_user.id == user_id:
        return forbidden_response("Cannot delete your own account")
    
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    
    if not success:
        return not_found_response("User not found")
    
    return success_response(
        message="User deleted successfully"
    )


@router.get("/roles/all", response_model=dict)
async def get_all_roles(
    current_user: User = Depends(require_admin_permission()),
    db: Session = Depends(get_db)
):
    \"\"\"
    Get all available roles
    Requires admin permission
    \"\"\"
    user_service = UserService(db)
    roles = user_service.get_all_roles()
    
    role_responses = [
        RoleResponse(id=role.id, name=role.name, description=role.description)
        for role in roles
    ]
    
    return success_response(
        data={"roles": [role.dict() for role in role_responses]},
        message="Roles retrieved successfully"
    )
"""

with open('app/api/users.py', 'w') as f:
    f.write(users_api_content)

# Create API __init__.py
api_init_content = """from app.api import auth, users

__all__ = ["auth", "users"]
"""

with open('app/api/__init__.py', 'w') as f:
    f.write(api_init_content)

print("✅ API endpoints created!")