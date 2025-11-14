"""
Authentication forms for login and registration.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, BooleanField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional, Regexp
from agrifarma.models.user import User


class LoginForm(FlaskForm):
    """Login form for user authentication."""
    
    username = StringField('Username or Email', 
                          validators=[DataRequired(), Length(min=3, max=80)])
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    """Registration form for new users."""
    
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
                            DataRequired(), 
                            Length(min=10, max=20),
                            Regexp('^[\d\s\-\+\(\)]+$', message='Invalid mobile number format')
                        ])
    
    # Location
    city = StringField('City', validators=[DataRequired(), Length(max=100)])
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
                            validators=[DataRequired()])
    
    expertise_level = SelectField('Expertise Level', 
                                 choices=[
                                     ('beginner', 'Beginner'),
                                     ('intermediate', 'Intermediate'),
                                     ('expert', 'Expert')
                                 ],
                                 validators=[DataRequired()])
    
    specialization = StringField('Specialization/Area of Interest', 
                                validators=[Optional(), Length(max=255)])
    bio = TextAreaField('Bio', validators=[Optional(), Length(max=500)])
    
    password = PasswordField('Password', 
                            validators=[
                                DataRequired(), 
                                Length(min=6, max=100),
                                Regexp('^(?=.*[A-Za-z])(?=.*\d)', 
                                      message='Password must contain at least one letter and one number')
                            ])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[
                                        DataRequired(), 
                                        EqualTo('password', message='Passwords must match')
                                    ])
    
    role = SelectField('I want to register as', 
                      choices=[
                          ('farmer', 'Farmer'),
                          ('consultant', 'Agricultural Consultant'),
                          ('vendor', 'Product Vendor')
                      ],
                      validators=[DataRequired()])
    
    # Farmer-specific fields
    farm_size = StringField('Farm Size (acres)', validators=[Optional()])
    crops_grown = StringField('Crops Grown', validators=[Optional(), Length(max=255)])
    farming_experience = StringField('Years of Farming Experience', validators=[Optional()])
    
    # Consultant-specific fields
    qualifications = TextAreaField('Qualifications & Certifications', validators=[Optional(), Length(max=1000)])
    consultation_fee = StringField('Consultation Fee (PKR)', validators=[Optional()])
    
    # Vendor-specific fields
    business_name = StringField('Business Name', validators=[Optional(), Length(max=150)])
    business_license = StringField('Business License Number', validators=[Optional(), Length(max=100)])

    # Optional profile picture at registration
    profile_picture = FileField('Profile Picture', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed!')
    ])
    
    def validate_username(self, username):
        """Check if username already exists."""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists. Please choose a different one.')
    
    def validate_email(self, email):
        """Check if email already exists."""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')
    
    def validate_mobile(self, mobile):
        """Check if mobile number already exists."""
        user = User.query.filter_by(mobile=mobile.data).first()
        if user:
            raise ValidationError('Mobile number already registered.')


class ForgotPasswordForm(FlaskForm):
    """Form for requesting password reset."""
    
    email = StringField('Email', 
                       validators=[DataRequired(), Email()])


class ResetPasswordForm(FlaskForm):
    """Form for resetting password."""
    
    password = PasswordField('New Password', 
                            validators=[
                                DataRequired(), 
                                Length(min=6, max=100),
                                Regexp('^(?=.*[A-Za-z])(?=.*\d)', 
                                      message='Password must contain at least one letter and one number')
                            ])
    confirm_password = PasswordField('Confirm Password', 
                                    validators=[
                                        DataRequired(), 
                                        EqualTo('password', message='Passwords must match')
                                    ])


class ChangePasswordForm(FlaskForm):
    """Form for changing password when logged in."""
    
    current_password = PasswordField('Current Password', 
                                    validators=[DataRequired()])
    new_password = PasswordField('New Password', 
                                validators=[
                                    DataRequired(), 
                                    Length(min=6, max=100),
                                    Regexp('^(?=.*[A-Za-z])(?=.*\d)', 
                                          message='Password must contain at least one letter and one number')
                                ])
    confirm_password = PasswordField('Confirm New Password', 
                                    validators=[
                                        DataRequired(), 
                                        EqualTo('new_password', message='Passwords must match')
                                    ])
