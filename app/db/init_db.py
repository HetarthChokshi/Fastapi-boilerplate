from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models import User, Role, Module, Permission, ModulePermission
from app.db.base import engine, Base


def create_tables():
    """Create all database tables"""
    Base.metadata.create_all(bind=engine)


def init_roles_and_permissions(db: Session):
    """Initialize roles, modules, and permissions with seed data"""
    
    # Create modules
    modules_data = [
        {"name": "users", "permissions": ["read", "write", "delete"]},
        {"name": "auth", "permissions": ["login", "logout", "refresh"]},
        {"name": "admin", "permissions": ["manage_users", "manage_roles"]},
    ]
    
    modules = {}
    for module_data in modules_data:
        module = db.query(Module).filter(Module.name == module_data["name"]).first()
        if not module:
            module = Module(name=module_data["name"])
            db.add(module)
            db.commit()
            db.refresh(module)
        modules[module_data["name"]] = module
    
    # Create permissions
    permissions = {}
    for module_data in modules_data:
        module = modules[module_data["name"]]
        for perm_name in module_data["permissions"]:
            permission = db.query(Permission).filter(
                Permission.name == perm_name,
                Permission.module_id == module.id
            ).first()
            if not permission:
                permission = Permission(
                    name=perm_name,
                    description=f"{perm_name.title()} permission for {module.name}",
                    module_id=module.id
                )
                db.add(permission)
                db.commit()
                db.refresh(permission)
            permissions[f"{module.name}:{perm_name}"] = permission
    
    # Create roles
    roles_data = [
        {
            "name": "superadmin",
            "description": "Super administrator with all permissions",
            "permissions": list(permissions.keys())
        },
        {
            "name": "admin", 
            "description": "Administrator with user management permissions",
            "permissions": ["users:read", "users:write", "users:delete", "auth:login", "auth:logout"]
        },
        {
            "name": "user",
            "description": "Regular user with basic permissions", 
            "permissions": ["auth:login", "auth:logout", "auth:refresh"]
        }
    ]
    
    for role_data in roles_data:
        role = db.query(Role).filter(Role.name == role_data["name"]).first()
        if not role:
            role = Role(name=role_data["name"], description=role_data["description"])
            db.add(role)
            db.commit()
            db.refresh(role)
            
            # Assign permissions to role
            for perm_key in role_data["permissions"]:
                if perm_key in permissions:
                    module_permission = ModulePermission(
                        role_id=role.id,
                        permission_id=permissions[perm_key].id
                    )
                    db.add(module_permission)
            
            db.commit()


def create_superadmin(db: Session):
    """Create superadmin user"""
    superadmin_role = db.query(Role).filter(Role.name == "superadmin").first()
    if not superadmin_role:
        raise ValueError("Superadmin role not found. Run init_roles_and_permissions first.")
    
    superadmin = db.query(User).filter(User.email == "admin@example.com").first()
    if not superadmin:
        superadmin = User(
            username="superadmin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            role_id=superadmin_role.id,
            is_active=True
        )
        db.add(superadmin)
        db.commit()
        db.refresh(superadmin)
        print("✅ Superadmin user created: admin@example.com / admin123")


def initialize_database():
    """Initialize database with tables and seed data"""
    from app.db.base import SessionLocal
    
    create_tables()
    
    db = SessionLocal()
    try:
        init_roles_and_permissions(db)
        create_superadmin(db)
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    initialize_database()