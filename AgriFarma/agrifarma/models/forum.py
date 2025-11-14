"""
Forum models for discussion board functionality.
Includes Category (with subcategories), Thread, and Reply models.
"""
from datetime import datetime
from agrifarma.extensions import db
from agrifarma.models.base import BaseModel


class Category(BaseModel):
    """
    Forum category model with support for subcategories.
    Implements hierarchical structure (e.g., Crops → Wheat → Diseases).
    """
    __tablename__ = 'forum_categories'
    
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='feather icon-folder')  # Feather icon class
    color = db.Column(db.String(20), default='primary')  # Bootstrap color class
    
    # Hierarchical structure
    parent_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'))
    parent = db.relationship('Category', remote_side='Category.id', backref='subcategories')
    
    # Display order
    position = db.Column(db.Integer, default=0)
    
    # Status
    is_active = db.Column(db.Boolean, default=True)
    is_locked = db.Column(db.Boolean, default=False)  # Locked categories can't have new threads
    
    # Relationships
    threads = db.relationship('Thread', backref='category', lazy='dynamic', 
                            cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Category {self.name}>'
    
    def get_thread_count(self):
        """Get total number of threads in this category and subcategories."""
        count = self.threads.filter_by(is_deleted=False).count()
        for subcat in self.subcategories:
            count += subcat.get_thread_count()
        return count
    
    def get_reply_count(self):
        """Get total number of replies in this category and subcategories."""
        count = sum(thread.replies.filter_by(is_deleted=False).count() 
                   for thread in self.threads.filter_by(is_deleted=False))
        for subcat in self.subcategories:
            count += subcat.get_reply_count()
        return count
    
    def get_latest_thread(self):
        """Get the most recent thread in this category or subcategories."""
        threads = list(self.threads.filter_by(is_deleted=False).order_by(Thread.created_at.desc()).limit(1))
        
        for subcat in self.subcategories:
            subcat_latest = subcat.get_latest_thread()
            if subcat_latest:
                threads.append(subcat_latest)
        
        if threads:
            return max(threads, key=lambda t: t.created_at)
        return None
    
    def get_breadcrumb(self):
        """Get breadcrumb trail for this category."""
        breadcrumb = [self]
        current = self.parent
        while current:
            breadcrumb.insert(0, current)
            current = current.parent
        return breadcrumb


class Thread(BaseModel):
    """
    Forum thread (discussion topic) model.
    """
    __tablename__ = 'forum_threads'
    
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref='threads', foreign_keys=[author_id])
    
    # Category
    category_id = db.Column(db.Integer, db.ForeignKey('forum_categories.id'), nullable=False)
    
    # Thread status
    is_pinned = db.Column(db.Boolean, default=False)  # Pinned threads appear at top
    is_locked = db.Column(db.Boolean, default=False)  # Locked threads can't receive replies
    is_deleted = db.Column(db.Boolean, default=False)  # Soft delete
    is_solved = db.Column(db.Boolean, default=False)  # Mark as solved
    
    # Statistics
    view_count = db.Column(db.Integer, default=0)
    
    # Timestamps
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    replies = db.relationship('Reply', backref='thread', lazy='dynamic',
                            cascade='all, delete-orphan', order_by='Reply.created_at')
    
    def __repr__(self):
        return f'<Thread {self.title}>'
    
    def get_reply_count(self):
        """Get number of non-deleted replies."""
        return self.replies.filter_by(is_deleted=False).count()
    
    def get_latest_reply(self):
        """Get the most recent non-deleted reply."""
        return self.replies.filter_by(is_deleted=False).order_by(Reply.created_at.desc()).first()
    
    def increment_views(self):
        """Increment view count."""
        self.view_count += 1
        db.session.commit()
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.utcnow()
        db.session.commit()
    
    def mark_as_solved(self):
        """Mark thread as solved."""
        self.is_solved = True
        db.session.commit()
    
    def soft_delete(self):
        """Soft delete the thread."""
        self.is_deleted = True
        db.session.commit()
    
    def restore(self):
        """Restore soft-deleted thread."""
        self.is_deleted = False
        db.session.commit()


class Reply(BaseModel):
    """
    Forum reply model for thread responses.
    """
    __tablename__ = 'forum_replies'
    
    content = db.Column(db.Text, nullable=False)
    
    # Author
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    author = db.relationship('User', backref='replies', foreign_keys=[author_id])
    
    # Thread
    thread_id = db.Column(db.Integer, db.ForeignKey('forum_threads.id'), nullable=False)
    
    # Reply status
    is_deleted = db.Column(db.Boolean, default=False)
    is_solution = db.Column(db.Boolean, default=False)  # Mark as solution to thread
    
    # Moderation
    is_edited = db.Column(db.Boolean, default=False)
    edited_at = db.Column(db.DateTime)
    edited_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    edited_by = db.relationship('User', foreign_keys=[edited_by_id])
    
    def __repr__(self):
        return f'<Reply {self.id} on Thread {self.thread_id}>'
    
    def soft_delete(self):
        """Soft delete the reply."""
        self.is_deleted = True
        db.session.commit()
    
    def restore(self):
        """Restore soft-deleted reply."""
        self.is_deleted = False
        db.session.commit()
    
    def mark_as_solution(self):
        """Mark this reply as the solution."""
        # Unmark other replies as solution
        for reply in self.thread.replies:
            if reply.is_solution and reply.id != self.id:
                reply.is_solution = False
        
        self.is_solution = True
        self.thread.mark_as_solved()
        db.session.commit()
