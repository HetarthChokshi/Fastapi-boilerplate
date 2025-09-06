from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Role relationship
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    role = relationship("Role", back_populates="users")
    
    # User-specific permissions
    user_permissions = relationship("UserPermission", back_populates="user")
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if user has a specific permission"""
        # Check role permissions
        for module_permission in self.role.module_permissions:
            if module_permission.permission.name == permission_name:
                return True
        
        # Check user-specific permissions
        for user_permission in self.user_permissions:
            if user_permission.permission.name == permission_name:
                return True
        
        return False
    
    def get_all_permissions(self) -> list:
        """Get all permissions for the user"""
        permissions = []
        
        # Role permissions
        for module_permission in self.role.module_permissions:
            permissions.append(module_permission.permission.name)
        
        # User-specific permissions
        for user_permission in self.user_permissions:
            permissions.append(user_permission.permission.name)
        
        return list(set(permissions))  # Remove duplicates
