from fastapi import APIRouter, Depends, HTTPException, status
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
    """
    Authenticate user and return JWT token
    """
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
    """
    Logout user (token invalidation would be handled by client or blacklist)
    """
    # In a production app, you might want to implement token blacklisting here
    # For now, we'll just return a success response
    return success_response(
        message=f"User {current_user.username} logged out successfully"
    )


@router.get("/me", response_model=dict)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
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
    """
    Refresh access token (generate new token with same claims)
    """
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
