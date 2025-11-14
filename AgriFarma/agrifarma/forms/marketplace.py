"""Forms for Marketplace flows (checkout, add product)."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DecimalField
from wtforms.validators import DataRequired, Length, Optional


class CheckoutForm(FlaskForm):
    full_name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=150)])
    phone = StringField('Phone', validators=[DataRequired(), Length(min=7, max=20)])
    address = TextAreaField('Shipping Address', validators=[DataRequired(), Length(min=5)])
    city = StringField('City', validators=[DataRequired(), Length(min=2, max=100)])
    state = StringField('State/Province', validators=[Optional(), Length(max=100)])
    postal_code = StringField('Postal Code', validators=[Optional(), Length(max=20)])
    payment_method = SelectField(
        'Payment Method',
        choices=[('cod', 'Cash on Delivery'), ('bank_transfer', 'Bank Transfer')],
        validators=[DataRequired()],
        default='cod'
    )
    notes = TextAreaField('Order Notes', validators=[Optional(), Length(max=1000)])
