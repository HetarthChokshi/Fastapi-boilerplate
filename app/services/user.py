from typing import List, Optional
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.role import Role
from app.schemas.user import UserCreate, UserUpdate, UserListResponse, UserResponse
from app.core.security import get_password_hash


class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.user_permissions)
        ).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.user_permissions)
        ).filter(User.email == email).first()
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).options(
            joinedload(User.role),
            joinedload(User.user_permissions)
        ).filter(User.username == username).first()
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        search: Optional[str] = None,
        role_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> UserListResponse:
        """Get list of users with filtering and pagination"""
        query = self.db.query(User).options(joinedload(User.role))
        
        # Apply filters
        if search:
            query = query.filter(
                (User.username.ilike(f"%{search}%")) |
                (User.email.ilike(f"%{search}%"))
            )
        
        if role_id is not None:
            query = query.filter(User.role_id == role_id)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        users = query.offset(skip).limit(limit).all()
        
        # Convert to response format
        user_responses = []
        for user in users:
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
            user_responses.append(user_response)
        
        pages = (total + limit - 1) // limit if limit > 0 else 1
        
        return UserListResponse(
            users=user_responses,
            total=total,
            page=(skip // limit) + 1 if limit > 0 else 1,
            size=len(user_responses),
            pages=pages
        )
    
    def create_user(self, user_create: UserCreate) -> User:
        """Create new user"""
        # Check if email already exists
        if self.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if username already exists
        if self.get_user_by_username(user_create.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # Check if role exists
        role = self.db.query(Role).filter(Role.id == user_create.role_id).first()
        if not role:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid role ID"
            )
        
        # Create user
        hashed_password = get_password_hash(user_create.password)
        db_user = User(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            role_id=user_create.role_id,
            is_active=user_create.is_active
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return db_user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Check email uniqueness if being updated
        if user_update.email and user_update.email != user.email:
            existing_user = self.get_user_by_email(user_update.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Check username uniqueness if being updated
        if user_update.username and user_update.username != user.username:
            existing_user = self.get_user_by_username(user_update.username)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already taken"
                )
        
        # Check role exists if being updated
        if user_update.role_id:
            role = self.db.query(Role).filter(Role.id == user_update.role_id).first()
            if not role:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid role ID"
                )
        
        # Update fields
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.db.commit()
        self.db.refresh(user) 
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Soft delete user (set is_active to False)"""
        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        
        return True
    
    def get_all_roles(self) -> List[Role]:
        """Get all available roles"""
        return self.db.query(Role).all()
