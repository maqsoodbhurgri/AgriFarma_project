"""
Blog models for knowledge base and article management.
Includes BlogPost, BlogCategory, and BlogComment models.
"""
from datetime import datetime
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel


class BlogCategory(BaseModel):
    """
    Blog category model for organizing posts by topic.
    """
    __tablename__ = 'blog_categories'
    
    name = db.Column(db.String(100), nullable=False, unique=True)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='feather icon-book')
    color = db.Column(db.String(20), default='primary')
    
    # Display order
    position = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    posts = db.relationship('BlogPost', backref='category', lazy='dynamic', 
                           cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<BlogCategory {self.name}>'
    
    def get_post_count(self):
        """Get number of published posts in this category."""
        return self.posts.filter_by(is_published=True, is_deleted=False).count()


class BlogPost(BaseModel):
    """
    Blog post model for articles and knowledge base content.
    """
    __tablename__ = 'blog_posts'
    
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    excerpt = db.Column(db.String(500))  # Short summary
    content = db.Column(db.Text, nullable=False)  # Full HTML content
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref='blog_posts', foreign_keys=[author_id])
    
    # Category
    category_id = db.Column(db.Integer, db.ForeignKey('blog_categories.id'))
    
    # Images
    featured_image = db.Column(db.String(255))  # Main post image
    
    # Tags (comma-separated)
    tags = db.Column(db.String(500))
    
    # Status
    is_published = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)  # Featured posts on homepage
    is_deleted = db.Column(db.Boolean, default=False)  # Soft delete
    
    # Publishing
    published_at = db.Column(db.DateTime)
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    like_count = db.Column(db.Integer, default=0)
    
    # SEO
    meta_description = db.Column(db.String(160))
    meta_keywords = db.Column(db.String(255))
    
    # Relationships
    comments = db.relationship('BlogComment', backref='post', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='BlogComment.created_at')
    likes = db.relationship('BlogLike', backref='post', lazy='dynamic',
                          cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<BlogPost {self.title}>'
    
    def publish(self):
        """Publish the blog post."""
        self.is_published = True
        self.published_at = datetime.utcnow()
        db.session.commit()
    
    def unpublish(self):
        """Unpublish the blog post."""
        self.is_published = False
        self.published_at = None
        db.session.commit()
    
    def get_comment_count(self):
        """Get number of non-deleted comments."""
        return self.comments.filter_by(is_deleted=False).count()
    
    def increment_views(self):
        """Increment view count."""
        self.view_count += 1
        db.session.commit()
    
    def soft_delete(self):
        """Soft delete the post."""
        self.is_deleted = True
        db.session.commit()
    
    def restore(self):
        """Restore soft-deleted post."""
        self.is_deleted = False
        db.session.commit()
    
    def get_tags_list(self):
        """Get tags as a list."""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_reading_time(self):
        """Estimate reading time in minutes (assuming 200 words/min)."""
        if not self.content:
            return 1
        word_count = len(self.content.split())
        reading_time = max(1, round(word_count / 200))
        return reading_time


class BlogComment(BaseModel):
    """
    Blog comment model for post comments.
    """
    __tablename__ = 'blog_comments'
    
    content = db.Column(db.Text, nullable=False)
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref='blog_comments', foreign_keys=[author_id])
    
    # Post
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    
    # Reply support
    parent_id = db.Column(db.Integer, db.ForeignKey('blog_comments.id'))
    parent = db.relationship('BlogComment', remote_side='BlogComment.id', backref='replies')
    
    # Status
    is_deleted = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)  # For moderation
    
    # Moderation
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<BlogComment {self.id} on Post {self.post_id}>'
    
    def soft_delete(self):
        """Soft delete the comment."""
        self.is_deleted = True
        db.session.commit()
    
    def restore(self):
        """Restore soft-deleted comment."""
        self.is_deleted = False
        db.session.commit()
    
    def approve(self):
        """Approve comment (for moderation)."""
        self.is_approved = True
        db.session.commit()
    
    def unapprove(self):
        """Unapprove comment."""
        self.is_approved = False
        db.session.commit()


class BlogLike(BaseModel):
    """
    Blog like model for tracking user likes on posts.
    """
    __tablename__ = 'blog_likes'
    
    # User who liked
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref='blog_likes')
    
    # Post that was liked
    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    
    # Ensure one like per user per post
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_like_uc'),)
    
    def __repr__(self):
        return f'<BlogLike User:{self.user_id} Post:{self.post_id}>'


class BlogAttachment(BaseModel):
    """
    File attachments associated with a blog post (images, videos, documents).
    """
    __tablename__ = 'blog_attachments'

    post_id = db.Column(db.Integer, db.ForeignKey('blog_posts.id'), nullable=False)
    post = db.relationship('BlogPost', backref=db.backref('attachments', lazy='dynamic', cascade='all, delete-orphan'))

    file_path = db.Column(db.String(255), nullable=False)  # relative to static/
    mime_type = db.Column(db.String(100))
    original_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)

    def __repr__(self):
        return f'<BlogAttachment {self.original_name or self.file_path}>'
