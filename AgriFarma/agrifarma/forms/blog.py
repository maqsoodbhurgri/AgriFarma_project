"""
Blog forms for creating posts, comments, and categories.
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Regexp


class BlogCategoryForm(FlaskForm):
    """Form for creating/editing blog categories (admin only)."""
    
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
    
    icon = StringField('Icon Class', 
                      validators=[Optional(), Length(max=50)],
                      default='feather icon-book',
                      render_kw={'placeholder': 'feather icon-book'})
    
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


class BlogPostForm(FlaskForm):
    """Form for creating/editing blog posts."""
    
    title = StringField('Post Title', 
                       validators=[DataRequired(), Length(min=5, max=200)],
                       render_kw={'placeholder': 'Enter an engaging title'})
    
    excerpt = TextAreaField('Excerpt', 
                           validators=[Optional(), Length(max=500)],
                           render_kw={
                               'rows': 3,
                               'placeholder': 'Short summary of the post (shown in listings)'
                           })
    
    category_id = SelectField('Category', 
                             coerce=int, 
                             validators=[Optional()])
    
    content = TextAreaField('Content', 
                           validators=[DataRequired(), Length(min=50)],
                           render_kw={
                               'rows': 20, 
                               'class': 'tinymce',
                               'placeholder': 'Write your article content here...'
                           })
    
    featured_image = FileField('Featured Image',
                              validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 
                                                    'Images only!')])
    attachments = FileField('Attachments',
                            render_kw={'multiple': True},
                            validators=[FileAllowed([
                                'jpg', 'jpeg', 'png', 'gif',
                                'mp4', 'mov', 'avi', 'mkv',
                                'pdf', 'ppt', 'pptx', 'doc', 'docx'
                            ], 'Unsupported file type')])
    
    tags = StringField('Tags', 
                      validators=[Optional(), Length(max=500)],
                      render_kw={'placeholder': 'agriculture, farming, tips (comma-separated)'})
    
    meta_description = StringField('Meta Description (SEO)', 
                                  validators=[Optional(), Length(max=160)],
                                  render_kw={'placeholder': 'Description for search engines'})
    
    meta_keywords = StringField('Meta Keywords (SEO)', 
                               validators=[Optional(), Length(max=255)],
                               render_kw={'placeholder': 'keywords, for, search, engines'})
    
    is_published = BooleanField('Publish Immediately', default=False)
    is_featured = BooleanField('Feature on Homepage', default=False)
    
    submit = SubmitField('Save Post')


class BlogCommentForm(FlaskForm):
    """Form for posting comments on blog posts."""
    
    content = TextAreaField('Your Comment', 
                           validators=[DataRequired(), Length(min=10, max=1000)],
                           render_kw={
                               'rows': 4, 
                               'placeholder': 'Share your thoughts...'
                           })
    
    submit = SubmitField('Post Comment')


class BlogSearchForm(FlaskForm):
    """Form for searching blog posts."""
    
    query = StringField('Search', 
                       validators=[DataRequired(), Length(min=2, max=100)],
                       render_kw={'placeholder': 'Search articles...'})
    
    category_id = SelectField('Category', 
                             coerce=int, 
                             validators=[Optional()])
    
    submit = SubmitField('Search')
