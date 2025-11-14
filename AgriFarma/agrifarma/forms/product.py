"""Forms for product management and reviews."""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, NumberRange, Optional

class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    slug = StringField('Slug', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    category = StringField('Category', validators=[DataRequired()])
    subcategory = StringField('Subcategory', validators=[Optional()])
    price = FloatField('Price (PKR)', validators=[DataRequired(), NumberRange(min=0)])
    original_price = FloatField('Original Price (PKR)', validators=[Optional(), NumberRange(min=0)])
    stock_quantity = IntegerField('Stock Quantity', validators=[DataRequired(), NumberRange(min=0)])
    sku = StringField('SKU', validators=[Optional()])
    unit = StringField('Unit', validators=[Optional()])
    weight = FloatField('Weight (kg)', validators=[Optional(), NumberRange(min=0)])
    brand = StringField('Brand', validators=[Optional()])
    manufacturer = StringField('Manufacturer', validators=[Optional()])
    image_url = StringField('Main Image URL', validators=[Optional()])
    is_active = BooleanField('Active')
    is_featured = BooleanField('Featured')
    submit = SubmitField('Save Product')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[('1','1'),('2','2'),('3','3'),('4','4'),('5','5')], validators=[DataRequired()])
    comment = TextAreaField('Comment', validators=[Optional()])
    submit = SubmitField('Submit Review')
