"""
User model for authentication and user management.
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel
from agrifarma.models.role import Role  # Re-export for tests expecting Role here


class User(UserMixin, BaseModel):
    """
    User model for managing user accounts.
    Supports multiple user types: admin, farmer, consultant, vendor.
    Enhanced with comprehensive profile fields.
    """
    __tablename__ = 'users'
    
    # Basic Information
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)  # Full name
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Contact Information
    mobile = db.Column(db.String(20))
    phone = db.Column(db.String(20))  # Alternative phone
    
    # Location Information
    city = db.Column(db.String(100))
    state = db.Column(db.String(100), default='Sindh')
    country = db.Column(db.String(100), default='Pakistan')
    address = db.Column(db.Text)
    
    # Professional Information
    profession = db.Column(db.String(50), default='farmer')  # farmer, academic, consultant, other
    expertise_level = db.Column(db.String(20), default='beginner')  # expert, intermediate, beginner
    specialization = db.Column(db.String(255))
    qualifications = db.Column(db.Text)
    bio = db.Column(db.Text)
    
    # Profile Media
    profile_picture = db.Column(db.String(255))
    profile_image = db.Column(db.String(255))  # Alias for backward compatibility
    
    # Role and Status
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    join_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime)
    
    # Password Reset
    reset_token = db.Column(db.String(100), unique=True)
    reset_token_expiry = db.Column(db.DateTime)
    
    # Farmer-specific fields
    farm_size = db.Column(db.Float)  # in acres
    crops_grown = db.Column(db.String(255))
    farming_experience = db.Column(db.Integer)  # years
    
    # Consultant-specific fields
    consultation_fee = db.Column(db.Float)
    
    # Vendor-specific fields
    business_name = db.Column(db.String(150))
    business_license = db.Column(db.String(100))
    
    # Community & Reputation
    reputation_score = db.Column(db.Integer, default=0)  # Forum reputation points
    
    def set_password(self, password):
        """Hash and set the user's password using Werkzeug."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)
    
    def get_reset_token(self, expires_sec=1800):
        """Generate a password reset token."""
        import secrets
        from datetime import timedelta
        
        self.reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(seconds=expires_sec)
        db.session.commit()
        return self.reset_token
    
    @staticmethod
    def verify_reset_token(token):
        """Verify and return user from reset token."""
        user = User.query.filter_by(reset_token=token).first()
        if user is None:
            return None
        if user.reset_token_expiry < datetime.utcnow():
            return None
        return user
    
    def clear_reset_token(self):
        """Clear the password reset token."""
        self.reset_token = None
        self.reset_token_expiry = None
        db.session.commit()
    
    def update_last_login(self):
        """Update the last login timestamp."""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        """Check if the user has admin role."""
        return self.role and self.role.name == 'admin'
    
    def is_farmer(self):
        """Check if the user has farmer role."""
        return self.role and self.role.name == 'farmer'
    
    def is_consultant(self):
        """Check if the user has consultant role."""
        return self.role and self.role.name == 'consultant'
    
    def is_vendor(self):
        """Check if the user has vendor role."""
        return self.role and self.role.name == 'vendor'

    # Generic role helper for templates expecting has_role()
    def has_role(self, role_name: str) -> bool:
        """Return True if user has the given role name.

        Added for template compatibility where `current_user.has_role('admin')` is used.
        Falls back gracefully if role is not loaded.
        """
        if not self.role or not role_name:
            return False
        return self.role.name == role_name
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def __str__(self):
        return self.username
