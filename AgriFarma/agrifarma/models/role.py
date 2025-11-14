"""
Role model for user role management.
"""
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel


class Role(BaseModel):
    """
    Role model for managing user roles (admin, farmer, consultant, vendor).
    """
    __tablename__ = 'roles'
    
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    
    # Relationship
    users = db.relationship('User', backref='role', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.name}>'
    
    def __str__(self):
        return self.name
