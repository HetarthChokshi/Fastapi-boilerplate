from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from jose import JWTError

from app.core.security import verify_password, create_access_token, verify_token
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import Token


class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.db.query(User).filter(User.email == email).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user
    
    def create_access_token_for_user(self, user: User) -> Token:
        """Create access token for authenticated user"""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        # Include user info and permissions in token
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role.name,
            "permissions": user.get_all_permissions()
        }
        
        access_token = create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )
        
        return Token(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def get_current_user_from_token(self, token: str) -> User:
        """Get current user from JWT token"""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = verify_token(token)
            if payload is None:
                raise credentials_exception
            
            user_id: str = payload.get("sub")
            if user_id is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = self.db.query(User).filter(User.id == int(user_id)).first()
        if user is None:
            raise credentials_exception
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        return user
    
    def check_user_permission(self, user: User, required_permission: str) -> bool:
        """Check if user has required permission"""
        # Superadmin has all permissions
        if user.role.name == "superadmin":
            return True
        
        return user.has_permission(required_permission)
