"""
Seed or update admin user with known password
"""
from agrifarma.extensions import db
from agrifarma.models.user import User
from agrifarma.models.role import Role
from app import app

def seed_admin():
    with app.app_context():
        admin_role = Role.query.filter_by(name="admin").first()
        if not admin_role:
            admin_role = Role(name="admin", description="Administrator")
            db.session.add(admin_role)
            db.session.commit()
        user = User.query.filter_by(email="admin@gmail.com").first()
        if not user:
            user = User(
                username="admin",
                name="Admin User",
                email="admin@gmail.com",
                role=admin_role,
                is_active=True,
                is_verified=True
            )
            user.set_password("admin123")
            db.session.add(user)
        else:
            user.set_password("admin123")
            user.role = admin_role
            user.is_active = True
            user.is_verified = True
        db.session.commit()
        print("Admin user created/updated: admin@gmail.com | password: admin123")

if __name__ == "__main__":
    seed_admin()
