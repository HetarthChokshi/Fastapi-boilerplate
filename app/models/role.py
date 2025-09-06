from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base


class Role(Base):
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(Text)
    
    # Relationships
    users = relationship("User", back_populates="role")
    module_permissions = relationship("ModulePermission", back_populates="role")


class Module(Base):
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)  
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    # Relationships
    permissions = relationship("Permission", back_populates="module")


class Permission(Base):
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    module_id = Column(Integer, ForeignKey("modules.id"), nullable=False)
    
    # Relationships
    module = relationship("Module", back_populates="permissions")
    module_permissions = relationship("ModulePermission", back_populates="permission")


class ModulePermission(Base):
    __tablename__ = "module_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    
    # Relationships
    role = relationship("Role", back_populates="module_permissions")
    permission = relationship("Permission", back_populates="module_permissions")


class UserPermission(Base):
    __tablename__ = "user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="user_permissions")
    permission = relationship("Permission")
