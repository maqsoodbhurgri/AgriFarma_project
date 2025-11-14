"""WTForms for consultancy module."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, BooleanField, DateField, TimeField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange


class ConsultantProfileForm(FlaskForm):
    specialization = StringField('Specialization', validators=[DataRequired()])
    bio = TextAreaField('Bio / Experience', validators=[Optional()])
    hourly_rate = FloatField('Hourly Rate (PKR)', validators=[Optional(), NumberRange(min=0)])
    available_online = BooleanField('Available for online consultation')
    submit = SubmitField('Save Profile')


class SlotCreateForm(FlaskForm):
    date = DateField('Date', validators=[DataRequired()])
    start_time = TimeField('Start Time', validators=[DataRequired()])
    duration_minutes = IntegerField('Duration (minutes)', validators=[DataRequired(), NumberRange(min=15, max=240)])
    price = FloatField('Price (PKR)', validators=[Optional(), NumberRange(min=0)])
    submit = SubmitField('Create Slot')


class BookingForm(FlaskForm):
    notes = TextAreaField('Notes / Goals', validators=[Optional()])
    submit = SubmitField('Confirm Booking')


class ContactConsultantForm(FlaskForm):
    subject = StringField('Subject', validators=[Optional()])
    message = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Send Message')
