"""
SRS Compliance tracking models.
Allows admins to manually override requirement statuses and add notes.
"""
from datetime import datetime
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel


class SRSModule(BaseModel):
    """
    Tracks SRS module compliance status with manual overrides.
    """
    __tablename__ = 'srs_modules'
    
    module_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    
    # Manual override status
    override_status = db.Column(db.String(20))  # 'completed', 'partial', 'missing', None
    notes = db.Column(db.Text)
    
    # Tracking
    last_scanned_at = db.Column(db.DateTime)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', backref='srs_module_updates', foreign_keys=[updated_by_id])
    
    def __repr__(self):
        return f'<SRSModule {self.module_id}>'


class SRSRequirement(BaseModel):
    """
    Tracks individual SRS requirement compliance with manual overrides.
    """
    __tablename__ = 'srs_requirements'
    
    requirement_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    module_id = db.Column(db.String(50), nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    
    # Manual override
    override_status = db.Column(db.String(20))  # 'completed', 'partial', 'missing', None
    notes = db.Column(db.Text)
    
    # Tracking
    last_scanned_at = db.Column(db.DateTime)
    updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.relationship('User', backref='srs_requirement_updates', foreign_keys=[updated_by_id])
    
    def __repr__(self):
        return f'<SRSRequirement {self.requirement_id}>'
