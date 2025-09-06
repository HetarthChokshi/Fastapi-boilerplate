from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, validator


class UserBase(BaseModel):
    username: str
    email: EmailStr
    is_active: Optional[bool] = True


class UserCreate(UserBase):
    password: str
    role_id: int
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role_id: Optional[int] = None


class UserResponse(UserBase):
    id: int
    role_id: int
    role_name: Optional[str] = None
    permissions: Optional[List[str]] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int


class RoleBase(BaseModel):
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class RoleResponse(RoleBase):
    id: int
    
    class Config:
        from_attributes = True


class PermissionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    module_name: str
    
    class Config:
        from_attributes = True


class ModuleResponse(BaseModel):
    id: int
    name: str
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True
