"""
Base model class with common fields and methods.
"""
from datetime import datetime
from agrifarma.extensions import db


class BaseModel(db.Model):
    """
    Base model class that includes common fields.
    All other models should inherit from this.
    """
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save the current instance to the database."""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the current instance from the database."""
        db.session.delete(self)
        db.session.commit()
    
    def update(self, **kwargs):
        """Update the current instance with the provided keyword arguments."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        db.session.commit()
        return self
