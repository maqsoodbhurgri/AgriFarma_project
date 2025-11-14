"""Consultancy models: consultant profiles, slots, bookings."""
from datetime import datetime
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel


class ConsultantProfile(BaseModel):
    """Profile for a consultant user."""
    __tablename__ = 'consultant_profiles'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    specialization = db.Column(db.String(255), index=True)
    bio = db.Column(db.Text)
    hourly_rate = db.Column(db.Float, default=0.0)
    rating = db.Column(db.Float, default=0.0)
    total_sessions = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    available_online = db.Column(db.Boolean, default=True)

    # Relationships
    user = db.relationship('User', backref=db.backref('consultant_profile', uselist=False))
    slots = db.relationship('ConsultationSlot', backref='profile', lazy='dynamic', cascade='all, delete-orphan')
    bookings = db.relationship('ConsultationBooking', backref='consultant_profile', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<ConsultantProfile user={self.user_id} specialization={self.specialization}>'


class ConsultationSlot(BaseModel):
    """Time slot available for booking."""
    __tablename__ = 'consultation_slots'

    consultant_profile_id = db.Column(db.Integer, db.ForeignKey('consultant_profiles.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='available')  # available, booked, cancelled
    price = db.Column(db.Float)  # can override hourly_rate

    # Relationship to bookings
    bookings = db.relationship('ConsultationBooking', backref='slot', lazy='dynamic', cascade='all, delete-orphan')

    def duration_minutes(self):
        return int((self.end_time - self.start_time).total_seconds() / 60)

    def __repr__(self):
        return f'<ConsultationSlot consultant={self.consultant_profile_id} {self.start_time.isoformat()}>'


class ConsultationBooking(BaseModel):
    """Booking of a slot by a user (farmer)."""
    __tablename__ = 'consultation_bookings'

    slot_id = db.Column(db.Integer, db.ForeignKey('consultation_slots.id'), nullable=False)
    consultant_profile_id = db.Column(db.Integer, db.ForeignKey('consultant_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    status = db.Column(db.String(20), default='pending')  # pending, confirmed, cancelled, completed
    notes = db.Column(db.Text)
    cancelled_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)

    # Relationships
    user = db.relationship('User', backref='consultation_bookings')

    def __repr__(self):
        return f'<ConsultationBooking slot={self.slot_id} user={self.user_id} status={self.status}>'


class ConsultancyMessage(BaseModel):
    """Simple message sent to a consultant profile by a user."""
    __tablename__ = 'consultancy_messages'

    consultant_profile_id = db.Column(db.Integer, db.ForeignKey('consultant_profiles.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    subject = db.Column(db.String(200))
    message = db.Column(db.Text, nullable=False)

    # Relationships
    sender = db.relationship('User')
    consultant = db.relationship('ConsultantProfile', backref=db.backref('messages', lazy='dynamic', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<ConsultancyMessage to={self.consultant_profile_id} from={self.user_id}>'
