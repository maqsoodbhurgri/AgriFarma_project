"""
Profile and user update forms.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, ValidationError, Regexp
from flask_login import current_user
from agrifarma.models.user import User


class EditProfileForm(FlaskForm):
    """Form for updating user profile."""
    
    username = StringField('Username', 
                          validators=[
                              DataRequired(), 
                              Length(min=3, max=80),
                              Regexp('^[A-Za-z0-9_]+$', message='Username must contain only letters, numbers, and underscores')
                          ])
    name = StringField('Full Name', 
                      validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', 
                       validators=[DataRequired(), Email(), Length(max=120)])
    mobile = StringField('Mobile Number', 
                        validators=[
                            Optional(), 
                            Length(min=10, max=20),
                            Regexp('^[\d\s\-\+\(\)]+$', message='Invalid mobile number format')
                        ])
    phone = StringField('Alternative Phone', 
                       validators=[Optional(), Length(max=20)])
    
    # Location Information
    city = StringField('City', validators=[Optional(), Length(max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=100)])
    country = StringField('Country', validators=[Optional(), Length(max=100)])
    address = TextAreaField('Address', validators=[Optional(), Length(max=500)])
    
    # Professional Information
    profession = SelectField('Profession', 
                            choices=[
                                ('farmer', 'Farmer'),
                                ('academic', 'Academic/Researcher'),
                                ('consultant', 'Agricultural Consultant'),
                                ('other', 'Other')
                            ],
                            validators=[Optional()])
    
    expertise_level = SelectField('Expertise Level', 
                                 choices=[
                                     ('beginner', 'Beginner'),
                                     ('intermediate', 'Intermediate'),
                                     ('expert', 'Expert')
                                 ],
                                 validators=[Optional()])
    
    specialization = StringField('Specialization/Area of Interest', 
                                validators=[Optional(), Length(max=255)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    qualifications = TextAreaField('Qualifications & Certifications', 
                                  validators=[Optional(), Length(max=1000)])
    
    # Profile Picture
    profile_picture = FileField('Profile Picture', 
                               validators=[
                                   FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 
                                              'Only image files are allowed!')
                               ])
    
    # Farmer-specific fields
    farm_size = StringField('Farm Size (acres)', validators=[Optional()])
    crops_grown = StringField('Crops Grown', validators=[Optional(), Length(max=255)])
    farming_experience = StringField('Years of Experience', validators=[Optional()])
    
    # Consultant-specific fields
    consultation_fee = StringField('Consultation Fee (PKR)', validators=[Optional()])
    
    # Vendor-specific fields
    business_name = StringField('Business Name', validators=[Optional(), Length(max=150)])
    business_license = StringField('Business License Number', validators=[Optional(), Length(max=100)])
    
    def validate_username(self, username):
        """Check if username already exists (excluding current user)."""
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists (excluding current user)."""
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('Email already registered. Please use a different one.')
    
    def validate_mobile(self, mobile):
        """Check if mobile already exists (excluding current user)."""
        if mobile.data and mobile.data != current_user.mobile:
            user = User.query.filter_by(mobile=mobile.data).first()
            if user:
                raise ValidationError('Mobile number already registered.')
    
    submit = SubmitField('Update Profile')


# Alias for backward compatibility
ProfileForm = EditProfileForm
