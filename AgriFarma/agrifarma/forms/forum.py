"""
Forum forms for creating categories, threads, and replies.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class CategoryForm(FlaskForm):
    """Form for creating/editing forum categories (admin only)."""
    
    name = StringField('Category Name', 
                      validators=[DataRequired(), Length(min=2, max=100)])
    
    slug = StringField('URL Slug', 
                      validators=[
                          DataRequired(), 
                          Length(min=2, max=100),
                          Regexp('^[a-z0-9-]+$', message='Slug must contain only lowercase letters, numbers, and hyphens')
                      ])
    
    description = TextAreaField('Description', 
                               validators=[Optional(), Length(max=500)])
    
    parent_id = SelectField('Parent Category', 
                           coerce=int, 
                           validators=[Optional()])
    
    icon = StringField('Icon Class', 
                      validators=[Optional(), Length(max=50)],
                      default='feather icon-folder',
                      render_kw={'placeholder': 'feather icon-folder'})
    
    color = SelectField('Color Theme', 
                       choices=[
                           ('primary', 'Primary Blue'),
                           ('success', 'Success Green'),
                           ('info', 'Info Cyan'),
                           ('warning', 'Warning Yellow'),
                           ('danger', 'Danger Red'),
                           ('secondary', 'Secondary Gray'),
                       ],
                       default='primary')
    
    position = StringField('Display Order', 
                          validators=[Optional()],
                          default='0',
                          render_kw={'type': 'number', 'min': '0'})
    
    is_active = BooleanField('Active', default=True)
    
    submit = SubmitField('Save Category')


class ThreadForm(FlaskForm):
    """Form for creating/editing forum threads."""
    
    title = StringField('Thread Title', 
                       validators=[DataRequired(), Length(min=5, max=200)],
                       render_kw={'placeholder': 'Enter a descriptive title for your discussion'})
    
    category_id = SelectField('Category', 
                             coerce=int, 
                             validators=[DataRequired()])
    
    content = TextAreaField('Content', 
                           validators=[DataRequired(), Length(min=10, max=10000)],
                           render_kw={
                               'rows': 10, 
                               'placeholder': 'Share your thoughts, questions, or experiences...'
                           })
    
    submit = SubmitField('Start Discussion')


class ReplyForm(FlaskForm):
    """Form for posting replies to threads."""
    
    content = TextAreaField('Your Reply', 
                           validators=[DataRequired(), Length(min=5, max=5000)],
                           render_kw={
                               'rows': 6, 
                               'placeholder': 'Write your reply...'
                           })
    
    submit = SubmitField('Post Reply')


class SearchForm(FlaskForm):
    """Form for searching forum threads."""
    
    query = StringField('Search', 
                       validators=[DataRequired(), Length(min=2, max=100)],
                       render_kw={'placeholder': 'Search discussions...'})
    
    category_id = SelectField('Category', 
                             coerce=int, 
                             validators=[Optional()])
    
    search_in = SelectField('Search In', 
                           choices=[
                               ('all', 'Titles and Content'),
                               ('title', 'Titles Only'),
                               ('content', 'Content Only')
                           ],
                           default='all')
    
    submit = SubmitField('Search')


class MoveThreadForm(FlaskForm):
    """Form for moving threads to different categories (admin/moderator)."""
    
    category_id = SelectField('Move to Category', 
                             coerce=int, 
                             validators=[DataRequired()])
    
    submit = SubmitField('Move Thread')


class EditThreadForm(FlaskForm):
    """Form for editing thread title and content."""
    
    title = StringField('Thread Title', 
                       validators=[DataRequired(), Length(min=5, max=200)])
    
    content = TextAreaField('Content', 
                           validators=[DataRequired(), Length(min=10, max=10000)],
                           render_kw={'rows': 10})
    
    submit = SubmitField('Update Thread')


class EditReplyForm(FlaskForm):
    """Form for editing replies."""
    
    content = TextAreaField('Reply Content', 
                           validators=[DataRequired(), Length(min=5, max=5000)],
                           render_kw={'rows': 6})
    
    submit = SubmitField('Update Reply')
